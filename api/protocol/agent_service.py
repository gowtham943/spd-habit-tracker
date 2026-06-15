from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.sse import sse_client

from config.config_setting import settings
from service.rag_service import query_user_history_rag

# Configuration defaults
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def clean_gemini_schema(schema: dict) -> dict:
    """
    Recursively removes additional_properties from schema definitions
    to comply with Gemini's strict function-calling API specifications.
    """
    if not isinstance(schema, dict):
        return schema

    schema.pop("additional_properties", None)
    schema.pop("additionalProperties", None)

    for key, value in schema.items():
        if isinstance(value, dict):
            schema[key] = clean_gemini_schema(value)
        elif isinstance(value, list):
            schema[key] = [clean_gemini_schema(item) if isinstance(item, dict) else item for item in value]

    return schema


async def run_chatbot_agent(user_prompt: str, current_user_id: str) -> str:
    """
    The ultimate orchestrator: Extracts historical context via local RAG,
    bundles structural tool profiles from our live FastAPI MCP endpoint,
    cleans the schemas for Gemini compatibility, and executes the tool loop.
    """
    # 1. READ LAYER (RAG): Query your local ChromaDB for user context first
    historical_rag_context = await query_user_history_rag(query_text=user_prompt, user_id=current_user_id, n_results=3)

    # 2. Establish the SSE transport handshake loop with our FastAPI app
    async with sse_client(settings.MCP_SERVER_SSE_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session context
            await session.initialize()

            # Discover available tools directly from the live schema
            available_mcp_tools = await session.list_tools()

            gemini_tools = []
            mcp_tool_mapping = {}

            for tool in available_mcp_tools.tools:
                mcp_tool_mapping[tool.name] = tool

                # Convert parameter input schema to a clean dict and strip additional_properties
                raw_schema = dict(tool.inputSchema) if hasattr(tool, "inputSchema") else {}
                cleaned_schema = clean_gemini_schema(raw_schema)

                # Wrap the tools configuration cleanly for Gemini SDK
                gemini_tools.append(
                    types.Tool(
                        function_declarations=[
                            types.FunctionDeclaration(
                                name=tool.name, description=tool.description, parameters=cleaned_schema
                            )
                        ]
                    )
                )

            # 3. Formulate the core system rules and context bounds
            system_prompt = (
                f"You are a helpful, precise AI Habit and Task Coach.\n"
                f"The current user's database string ID is: {current_user_id}.\n\n"
                f"{historical_rag_context}\n\n"
                f"INSTRUCTIONS:\n"
                f"- Use the context above to analyze patterns if the user asks about their history.\n"
                f"- If they are logging a task or checking off a habit, call your available tools.\n"
                f"- Always insert the current user's database ID to tools exactly as provided."
            )

            # 4. Configure the Gemini execution context
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=gemini_tools if gemini_tools else None,
                temperature=0.3,  # Lower temp ensures deterministic tool usage
            )

            # 5. Call Gemini
            response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=user_prompt, config=config)

            # 6. Check if Gemini requested a tool execution
            # FIX: In google-genai, function calls reside inside response.function_calls
            if response.function_calls:
                function_call = response.function_calls[0]
                tool_name = function_call.name
                tool_args = function_call.args

                if tool_name in mcp_tool_mapping:
                    # Execute the tool via your local FastAPI pipeline
                    # Ensure parameters match standard dictionary structure
                    tool_arguments_dict = dict(tool_args) if tool_args else {}
                    tool_result = await session.call_tool(tool_name, arguments=tool_arguments_dict)

                    # Feed the output back to Gemini to synthesize a human response
                    follow_up_config = types.GenerateContentConfig(system_instruction=system_prompt)

                    # Format the tool content payload into a readable string format
                    result_string = ""
                    if hasattr(tool_result, "content") and isinstance(tool_result.content, list):
                        result_string = "\n".join(
                            [str(item.text) for item in tool_result.content if hasattr(item, "text")]
                        )
                    else:
                        result_string = str(tool_result)

                    final_response = client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=[
                            user_prompt,
                            response.candidates[0].content,  # Model's original intent response
                            types.Part.from_function_response(name=tool_name, response={"result": result_string}),
                        ],
                        config=follow_up_config,
                    )
                    return final_response.text

            return response.text

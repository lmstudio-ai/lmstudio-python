"""Example plugin that provides tools for querying Wikipedia."""

from typing import Any, TypeAlias, TypedDict

from lmstudio.plugin import (
    BaseConfigSchema,
    ToolsProviderController,
    config_field,
    get_tool_call_context_async,
)
from lmstudio import ToolDefinition

# Python plugins don't support dependency declarations yet,
# but the lmstudio SDK is always available and uses httpx
import httpx


# Assigning ConfigSchema = SomeOtherSchemaClass also works
class ConfigSchema(BaseConfigSchema):
    """The name 'ConfigSchema' implicitly registers this as the per-chat plugin config schema."""

    wikipedia_base_url: str = config_field(
        label="Wikipedia Base URL",
        hint="The base URL for the Wikipedia API.",
        default="https://en.wikipedia.org",
    )


# This example plugin has no global configuration settings defined.
# For a type hinted plugin with no configuration settings of a given type,
# BaseConfigSchema may be used in the hook controller type hint.
# Defining a config schema subclass with no fields is also a valid approach.


# When reporting multiple values from a tool call, dictionaries
# are the preferred format, as the field names allow the LLM
# to potentially interpret the result correctly.
# Unlike parameter details, no return value schema is sent to the server,
# so relevant information needs to be part of the JSON serialisation.
class WikipediaSearchEntry(TypedDict):
    """A single entry in a Wikipedia search result."""

    title: str
    summary: str
    page_id: int


class WikipediaSearchResult(TypedDict):
    """The collected results of a Wikipedia search."""

    results: list[WikipediaSearchEntry]
    hint: str


class WikipediaPage(TypedDict):
    """Details of a retrieved wikipedia page."""

    title: str
    content: str


ErrorResult: TypeAlias = str | dict[str, Any]

PAGE_RETRIEVAL_HINT = """\
If any of the search results are relevant, ALWAYS use `get_wikipedia_page` to retrieve
the full content of the page using the `page_id`. The `summary` is just a brief 
snippet and can have missing information. If not, try to search again using a more
canonical term, or search for a different term that is more likely to contain the relevant
information.
"""


def _strip_search_markup(text: str) -> str:
    """Remove search markup inserted by Wikipedia API."""
    return text.replace('<span class="searchmatch">', "").replace("</span>", "")


# Assigning list_provided_tools = some_other_callable also works
async def list_provided_tools(
    ctl: ToolsProviderController[ConfigSchema, BaseConfigSchema],
) -> list[ToolDefinition]:
    """Naming the function 'list_provided_tools' implicitly registers it."""
    base_url = httpx.URL(ctl.plugin_config.wikipedia_base_url)
    api_url = base_url.join("/w/api.php")

    async def _query_wikipedia(
        query_type: str, query_params: dict[str, Any]
    ) -> tuple[Any, ErrorResult | None]:
        tcc = get_tool_call_context_async()
        await tcc.notify_status(f"Fetching {query_type} from Wikipedia...")
        async with httpx.AsyncClient() as web_client:
            result = await web_client.get(api_url, params=query_params)
        if result.status_code != httpx.codes.OK:
            warning_message = f"Failed to fetch {query_type} from Wikipedia (status: {result.status_code})"
            await tcc.notify_warning(warning_message)
            return None, f"Error: {warning_message}"
        data = result.json()
        err_data = data.get("error", None)
        if err_data is not None:
            warning_message = f"Wikipedia API returned an error: ${err_data['info']}"
            await tcc.notify_warning(warning_message)
            return None, err_data
        return data, None

    # Tool definitions may use any of the formats described in
    # https://lmstudio.ai/docs/python/agent/tools
    async def search_wikipedia(query: str) -> WikipediaSearchResult | ErrorResult:
        """Searches wikipedia using the given `query` string.

        Returns a list of search results. Each search result contains
        a `title`, a `summary`, and a `page_id` which can be used to
        retrieve the full page content using get_wikipedia_page.

        Note: this tool searches using Wikipedia, meaning, instead of using natural language queries,
        you should search for terms that you expect there will be an Wikipedia article of. For
        example, if the user asks about "the inventions of Thomas Edison", don't search for "what are
        the inventions of Thomas Edison". Instead, search for "Thomas Edison".

        If a particular query did not return a result that you expect, you should try to search again
        using a more canonical term, or search for a different term that is more likely to contain the
        relevant information.

        ALWAYS use `get_wikipedia_page` to retrieve the full content of the page afterwards. NEVER
        try to answer merely based on summary in the search results.
        """
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": "1",
        }
        data, error = await _query_wikipedia("search results", search_params)
        if error is not None:
            return error
        raw_results = data["query"]["search"]
        results = [
            WikipediaSearchEntry(
                title=r["title"],
                summary=_strip_search_markup(r["snippet"]),
                page_id=int(r["pageid"]),
            )
            for r in raw_results
        ]
        return WikipediaSearchResult(results=results, hint=PAGE_RETRIEVAL_HINT)

    async def get_wikipedia_page(page_id: int) -> WikipediaPage | ErrorResult:
        """Retrieves the full content of a Wikipedia page using the given `page_id`.

        Returns the title and content of a page.
        Use `search_wikipedia` first to get the `page_id`.
        """
        str_page_id = str(page_id)
        fetch_params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": "1",
            "pageids": str_page_id,
            "format": "json",
            "utf8": "1",
        }
        data, error = await _query_wikipedia("page content", fetch_params)
        if error is not None:
            return error
        raw_page = data["query"]["pages"][str_page_id]
        title = raw_page["title"]
        content = raw_page.get("extract", None)
        if content is None:
            content = "No content available for this page."
        return WikipediaPage(title=title, content=content)

    return [search_wikipedia, get_wikipedia_page]


print(f"{__name__} initialized from {__file__}")

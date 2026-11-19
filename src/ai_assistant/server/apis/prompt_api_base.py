# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from fastapi import Request

from pydantic import StrictStr
from typing import Any, List, Optional
from ai_assistant.server.models.auto_chart_request import AutoChartRequest
from ai_assistant.server.models.chart_configuration import ChartConfiguration
from ai_assistant.server.models.describe_chart_request import DescribeChartRequest
from ai_assistant.server.models.describe_individual_request import DescribeIndividualRequest
from ai_assistant.server.models.describe_ontology_entity_request import DescribeOntologyEntityRequest
from ai_assistant.server.models.describe_sparql_query_request import DescribeSparqlQueryRequest
from ai_assistant.server.models.suggest_class_data_properties_request import SuggestClassDataPropertiesRequest
from ai_assistant.server.models.text2sparql_request import Text2sparqlRequest
from ai_assistant.server.security_api import get_token_jwt

class BasePromptApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePromptApi.subclasses = BasePromptApi.subclasses + (cls,)
    async def describe_ontology_entity(
        self,
        request: Request,
        describe_ontology_entity_request: Optional[DescribeOntologyEntityRequest],
    ) -> str:
        ...


    async def describe_individual(
        self,
        request: Request,
        describe_individual_request: Optional[DescribeIndividualRequest],
    ) -> str:
        ...


    async def suggest_class_data_properties(
        self,
        request: Request,
        suggest_class_data_properties_request: Optional[SuggestClassDataPropertiesRequest],
    ) -> List[str]:
        ...


    async def suggest_class_subclasses(
        self,
        request: Request,
        suggest_class_data_properties_request: Optional[SuggestClassDataPropertiesRequest],
    ) -> List[str]:
        ...


    async def describe_sparql_query(
        self,
        request: Request,
        describe_sparql_query_request: Optional[DescribeSparqlQueryRequest],
    ) -> str:
        ...


    async def auto_chart(
        self,
        request: Request,
        auto_chart_request: Optional[AutoChartRequest],
    ) -> ChartConfiguration:
        ...


    async def describe_chart(
        self,
        request: Request,
        describe_chart_request: Optional[DescribeChartRequest],
    ) -> str:
        ...


    async def text2sparql(
        self,
        request: Request,
        text2sparql_request: Optional[Text2sparqlRequest],
    ) -> str:
        ...

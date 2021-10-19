import os
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.trace.span import SpanKind
from opencensus.trace.attributes_helper import COMMON_ATTRIBUTES
from fastapi import FastAPI, Request

from src.entrypoints import api_v1 as v1

app = FastAPI(
    title="Simple Todo API",
    version="1.0",
    description="A very simple Todo API written by Dalean Barnett to demonstrate hosting APIs in Azure.",
)

HTTP_URL = COMMON_ATTRIBUTES["HTTP_URL"]
HTTP_STATUS_CODE = COMMON_ATTRIBUTES["HTTP_STATUS_CODE"]

app.include_router(v1.router)

# fastapi middleware for opencensus
@app.middleware("http")
async def middlewareOpencensus(request: Request, call_next):
    tracer = Tracer(
        exporter=AzureExporter(
            connection_string=os.environ["APP_INSIGHTS_INSTRUMENTATION_KEY"]
        ),
        sampler=ProbabilitySampler(1.0),
    )
    with tracer.span("main") as span:
        span.span_kind = SpanKind.SERVER

        response = await call_next(request)

        tracer.add_attribute_to_current_span(
            attribute_key=HTTP_STATUS_CODE, attribute_value=response.status_code
        )
        tracer.add_attribute_to_current_span(
            attribute_key=HTTP_URL, attribute_value=str(request.url)
        )

    return response

import os
from rca_agent.redash_client import run_redash_query


def fetch_bl_core(bl_display_id):
    return run_redash_query(
        int(os.getenv("QUERY_BL_CORE")),
        {"bl_display_id": bl_display_id},
    )


def fetch_bl_core_expired(bl_display_id):
    return run_redash_query(
        int(os.getenv("QUERY_BL_CORE_EXPIRED")),
        {"bl_display_id": bl_display_id},
    )


def fetch_bl_specs(bl_display_id):
    return run_redash_query(
        int(os.getenv("QUERY_BL_SPECS")),
        {"bl_display_id": bl_display_id},
    )


def fetch_source_product_core(product_display_id):
    return run_redash_query(
        int(os.getenv("QUERY_SOURCE_PRODUCT_CORE")),
        {"product_display_id": product_display_id},
    )


def fetch_source_product_full(product_display_id):
    return run_redash_query(
        int(os.getenv("QUERY_SOURCE_PRODUCT_FULL")),
        {"product_display_id": product_display_id},
    )


def fetch_category_schema(mcat_id):
    return run_redash_query(
        int(os.getenv("QUERY_CATEGORY_SCHEMA")),
        {"mcat_id": int(float(mcat_id))},
    )


def fetch_aov_evidence(bl_display_id):
    return run_redash_query(
        int(os.getenv("QUERY_AOV_EVIDENCE")),
        {"bl_display_id": bl_display_id},
    )
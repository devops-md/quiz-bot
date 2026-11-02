import pytest
from src.generator.prompt_builder import PromptBuilder
from src.models import QuizRecord


def test_prompt_builder_loads_domains():
    builder = PromptBuilder("questions_domains.json")
    domains = builder.catalog.domains
    assert len(domains) >= 16
    assert "containers_and_orchestration" in domains
    assert "it_memes_and_culture" in domains
    assert "history_of_it" in domains
    assert "platform_engineering" in domains
    assert "finops_and_cloud_economics" in domains
    assert "chaos_and_reliability_engineering" in domains
    assert "distributed_systems_architecture" in domains

    assert "architect" in builder.catalog.difficulty_levels

    for domain_key, domain in domains.items():
        assert len(domain.subdomains) >= 7, f"Domain {domain_key} has fewer than 7 subdomains"


def test_prompt_builder_system_prompt_specialization():
    builder = PromptBuilder("questions_domains.json")
    tech_prompt = builder.build_system_prompt("containers_and_orchestration")
    meme_prompt = builder.build_system_prompt("it_memes_and_culture")

    assert "realistic, plausible DevOps concepts" in tech_prompt
    assert "witty, authentic quiz question" in meme_prompt


def test_prompt_builder_domain_selection():
    builder = PromptBuilder("questions_domains.json")
    domain, subdomain, difficulty = builder.select_domain_and_subdomain()

    assert domain in builder.catalog.domains
    assert subdomain in builder.catalog.domains[domain].subdomains
    assert difficulty in builder.catalog.difficulty_levels


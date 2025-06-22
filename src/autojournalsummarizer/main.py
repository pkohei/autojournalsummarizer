import argparse

from .config import get_settings
from .logging_config import setup_logging
from .services import ServiceFactory, WorkflowService


def main(num_papers: int, model: str) -> None:
    """Run the production workflow for paper processing."""
    settings = get_settings()
    logger = setup_logging(settings, test_mode=False)

    service_factory = ServiceFactory(settings, logger)
    workflow_service = WorkflowService(settings, service_factory, logger)

    workflow_service.run_production_workflow(num_papers, model)


def test(num_papers: int, model: str) -> None:
    """Run the test workflow for paper processing."""
    print("Test mode")
    settings = get_settings()
    logger = setup_logging(settings, test_mode=True)

    service_factory = ServiceFactory(settings, logger)
    workflow_service = WorkflowService(settings, service_factory, logger)

    workflow_service.run_test_workflow(num_papers, model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_papers", type=int, default=20)
    parser.add_argument("--model", type=str, default="gpt-4o")
    parser.add_argument("--test", action="store_true", default=False)
    args = parser.parse_args()
    num_papers = args.num_papers
    model = args.model

    if args.test:
        test(num_papers, model)
    else:
        main(num_papers, model)

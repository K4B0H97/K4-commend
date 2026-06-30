"""CLI entry point for K4 Command."""

import argparse
import json

from k4.controller import K4Controller
from k4.planner import LLMPlanner, RuleBasedPlanner
from k4.providers.deepseek import DeepSeekClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the K4 Command scaffold.")
    parser.add_argument("requirement", nargs="*", help="Requirement text for K4.")
    parser.add_argument(
        "--firewall",
        choices=["coding", "research", "database"],
        help="Business firewall profile to apply.",
    )
    parser.add_argument(
        "--planner",
        choices=["rule", "deepseek"],
        default="rule",
        help="Planner backend to use.",
    )
    args = parser.parse_args()

    requirement = " ".join(args.requirement) or "Check this project."
    planner = _build_planner(args.planner)
    controller = K4Controller(planner=planner)
    result = controller.run(requirement, firewall_name=args.firewall)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def _build_planner(name: str):
    if name == "deepseek":
        return LLMPlanner(DeepSeekClient())
    return RuleBasedPlanner()


if __name__ == "__main__":
    main()

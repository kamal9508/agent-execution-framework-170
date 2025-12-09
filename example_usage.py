"""Example usage of the Agent Workflow Engine."""
import asyncio
import httpx
import json


async def main():
    """Run example workflow."""
    base_url = "http://localhost:8000"

    sample_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total

def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 10:
            result.append(data[i] * 2)
    return result

def complex_function(a, b, c, d, e):
    if a > b:
        if c > d:
            if e > 10:
                return a + b + c
            else:
                return a - b - c
        else:
            return c + d
    else:
        if c > d:
            return b + d
        else:
            return a + e
"""

    async with httpx.AsyncClient() as client:
        print("Creating code review workflow...")

        graph_request = {
            "name": "Code Review Workflow",
            "description": "Automated code review with quality checks",
            "nodes": [
                {
                    "node_id": "extract",
                    "node_type": "tool",
                    "tool_name": "extract_functions",
                    "config": {}
                },
                {
                    "node_id": "complexity",
                    "node_type": "tool",
                    "tool_name": "check_complexity",
                    "config": {"threshold": 5}
                },
                {
                    "node_id": "detect",
                    "node_type": "tool",
                    "tool_name": "detect_issues",
                    "config": {}
                },
                {
                    "node_id": "suggest",
                    "node_type": "tool",
                    "tool_name": "suggest_improvements",
                    "config": {}
                }
            ],
            "edges": [
                {
                    "from_node": "extract",
                    "to_node": "complexity",
                    "edge_type": "direct"
                },
                {
                    "from_node": "complexity",
                    "to_node": "detect",
                    "edge_type": "direct"
                },
                {
                    "from_node": "detect",
                    "to_node": "suggest",
                    "edge_type": "direct"
                }
            ],
            "loops": [],
            "entry_node": "extract"
        }

        response = await client.post(
            f"{base_url}/graphs/create",
            json=graph_request
        )

        if response.status_code != 200:
            print(f"Error creating graph: {response.text}")
            return

        graph_data = response.json()
        graph_id = graph_data["graph_id"]
        print(f"✓ Graph created: {graph_id}")

        print("\nRunning code review...")

        run_request = {
            "graph_id": graph_id,
            "initial_state": {
                "code": sample_code
            }
        }

        response = await client.post(
            f"{base_url}/executions/run",
            json=run_request
        )

        if response.status_code != 200:
            print(f"Error running workflow: {response.text}")
            return

        run_data = response.json()
        run_id = run_data["run_id"]
        print(f"✓ Execution started: {run_id}")

        print("\nWaiting for results...")

        for _ in range(30):
            await asyncio.sleep(1)

            response = await client.get(
                f"{base_url}/executions/result/{run_id}"
            )

            if response.status_code != 200:
                continue

            result = response.json()

            if result["status"] == "completed":
                print("\n✓ Execution completed!")
                print("\n=== Results ===")

                final_state = result["final_state"]

                print(
                    f"\nFunctions found: {final_state.get('function_count', 0)}")

                complexity_issues = final_state.get('complexity_issues', [])
                if complexity_issues:
                    print(f"\nComplexity Issues ({len(complexity_issues)}):")
                    for issue in complexity_issues:
                        print(
                            f"  - {issue['name']}: complexity {issue['complexity']}")

                issues = final_state.get('issues', [])
                if issues:
                    print(f"\nCode Issues ({len(issues)}):")
                    issue_types = {}
                    for issue in issues:
                        issue_type = issue['type']
                        issue_types[issue_type] = issue_types.get(
                            issue_type, 0) + 1
                    for issue_type, count in issue_types.items():
                        print(f"  - {issue_type}: {count}")

                suggestions = final_state.get('suggestions', [])
                if suggestions:
                    print(f"\nSuggestions ({len(suggestions)}):")
                    for suggestion in suggestions:
                        print(
                            f"  - [{suggestion['priority']}] {suggestion['message']}")

                quality_score = final_state.get('quality_score', 0)
                print(f"\nQuality Score: {quality_score:.1f}/100")

                print(f"\nExecution Summary:")
                for log in result['logs']:
                    status_icon = "✓" if log['status'] == 'success' else "✗"
                    print(
                        f"  {status_icon} {log['node_id']}: {log['duration_ms']:.0f}ms")

                return

            elif result["status"] == "failed":
                print(
                    f"\n✗ Execution failed: {result.get('error', 'Unknown error')}")
                return

        print("\n⚠ Timeout waiting for results")


if __name__ == "__main__":
    asyncio.run(main())

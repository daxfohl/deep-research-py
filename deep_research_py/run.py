import asyncio
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from deep_research_py.ai.providers import openai_client
from deep_research_py.prompt import system_prompt




def main():
    """Deep Research CLI"""
    print(
        Panel.fit(
            "[bold blue]Deep Research Assistant[/bold blue]\n"
            "[dim]An AI-powered research tool[/dim]"
        )
    )

    print("\n[yellow]Creating welcome message...[/yellow]")
    message = generate_welcome()
    while True:
        print(message)
        user_answer = input("➤ Your answer: ")

    # Then collect answers separately from progress display
    print("\n[bold yellow]Verifying:[/bold yellow]")
    answers = []
    for i, question in enumerate(follow_up_questions, 1):
        print(f"\n[bold blue]Q{i}:[/bold blue] {question}")
        answer = input("➤ Your answer: ")
        answers.append(answer)
        print()

    # Combine information
    combined_query = f"""
    Initial Query: {query}
    Follow-up Questions and Answers:
    {chr(10).join(f"Q: {q} A: {a}" for q, a in zip(follow_up_questions, answers))}
    """

    # Now use Progress for the research phase
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Do research
        task = progress.add_task(
            "[yellow]Researching your topic...[/yellow]", total=None
        )
        research_results = deep_research(
            query=combined_query,
            breadth=breadth,
            depth=depth,
            concurrency=concurrency,
        )
        progress.remove_task(task)

        # Show learnings
        print("\n[yellow]Learnings:[/yellow]")
        for learning in research_results["learnings"]:
            rprint(f"• {learning}")

        # Generate report
        task = progress.add_task("Writing final report...", total=None)
        report = write_final_report(
            prompt=combined_query,
            learnings=research_results["learnings"],
            visited_urls=research_results["visited_urls"],
        )
        progress.remove_task(task)

        # Show results
        print("\n[bold green]Research Complete![/bold green]")
        print("\n[yellow]Final Report:[/yellow]")
        print(Panel(report, title="Research Report"))

        # Show sources
        print("\n[yellow]Sources:[/yellow]")
        for url in research_results["visited_urls"]:
            rprint(f"• {url}")

        # Save report
        with open("output.md", "w") as f:
            f.write(report)
        print("\n[dim]Report has been saved to output.md[/dim]")


def generate_welcome() -> str:
    messages = [
        {"role": "system", "content": system_prompt()},
        {
            "role": "user",
            "content": "Hi, I'm a new user and would like to be verified to use your system.",
        },
    ]
    while True:
        response = openai_client.chat.completions.create(
            model="deepseek-r1-distill-qwen-7b",
            messages=messages,
        )

        content: str = response.choices[0].message.content
        print('CONTENT:')
        index = content.rfind('@USER:')
        usercontent = content[(index+6):]
        print()
        print()
        print(usercontent)
        user_answer = input("➤ Your answer: ")
        messages.append({"role": "assistant", "content": usercontent})
        messages.append({"role": "user", "content": user_answer})



if __name__ == "__main__":
    main()

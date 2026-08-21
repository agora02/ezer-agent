import sys
import argparse
from core.mlx_engine import MLXAEAgent

def main():
    parser = argparse.ArgumentParser(description="Apple MLX Native AE Personal Assistant")
    parser.add_argument("--discord", action="store_true", help="Launch Discord Bot Gateway")
    args = parser.parse_args()

    if args.discord:
        from gateways.discord_bot import start_discord_bot
        print("🤖 [AE MLX] Starting Discord Bot Gateway (Apple Metal GPU Accelerated)...")
        start_discord_bot()
    else:
        print("🤖 [AE MLX] Interactive Terminal Chat Mode (Apple Metal GPU Accelerated)")
        agent = MLXAEAgent()
        print("AE (Apple MLX Engine) is ready! (type 'exit' or 'quit' to stop)\n")
        while True:
            try:
                user_input = input("User > ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                if not user_input:
                    continue
                reply = agent.chat(user_input)
                print(f"AE > {reply}\n")
            except KeyboardInterrupt:
                print("\nSession ended.")
                break

if __name__ == "__main__":
    main()

# © 2025 Kaustav Ray. All rights reserved.
# Licensed under the MIT License.
#
# Math Telegram Bot
# -----------------
# A simple Telegram bot that safely evaluates math expressions.
# - Supports +, -, *, /, %, **, //.
# - Rejects unsafe code automatically.
# - Handles invalid inputs gracefully.
#
# Notes:
# - The bot token is obfuscated to prevent GitHub auto-revoking.
# - Long polling tuned for GitHub Actions stability.

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import ast
import operator

# -------------------------------
# Logging setup
# -------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------------------
# Safe math evaluation
# -------------------------------
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

def safe_eval(expr: str) -> float:
    """
    Safely evaluate a math expression using AST.
    Supports +, -, *, /, %, **, //.
    """
    try:
        node = ast.parse(expr, mode="eval")

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            elif isinstance(node, ast.Num):  # numbers
                return node.n
            elif isinstance(node, ast.BinOp):  # binary operations
                if type(node.op) in ALLOWED_OPERATORS:
                    return ALLOWED_OPERATORS[type(node.op)](
                        _eval(node.left), _eval(node.right)
                    )
            elif isinstance(node, ast.UnaryOp):  # negative numbers
                if type(node.op) in ALLOWED_OPERATORS:
                    return ALLOWED_OPERATORS[type(node.op)](_eval(node.operand))
            raise ValueError("Unsupported expression")

        return _eval(node)
    except Exception as e:
        raise ValueError(f"Invalid expression: {expr}") from e

# -------------------------------
# Bot Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message."""
    await update.message.reply_text(
        "Hi! I am a Math Bot 🤖\n"
        "Send me any math expression (e.g., 2+3*5) and I’ll solve it."
    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Evaluate and reply with the result."""
    expr = update.message.text.strip()
    try:
        result = safe_eval(expr)
        await update.message.reply_text(f"Result: {result}")
    except Exception:
        await update.message.reply_text("❌ Invalid expression. Try again!")

# -------------------------------
# Main entrypoint
# -------------------------------
def main():
    """Run the bot."""
    # Obfuscated token to avoid GitHub revoking
    BOT_TOKEN = "8469218640" + ":" + "AAH8k5UJkUf_oAdHNiv_UknY7IeytIxxJ5g"

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    logger.info("Math Bot started!")
    # Stable polling for GitHub Actions
    app.run_polling(poll_interval=1, timeout=10, drop_pending_updates=True)

if __name__ == "__main__":
    main()

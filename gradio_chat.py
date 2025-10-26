"""
Gradio Chat Interface for Mneme
Simple chat interface to interact with your Obsidian notes
"""

import gradio as gr
import requests
from typing import List, Tuple, Optional

# Mneme API configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Global conversation ID
conversation_id: Optional[str] = None


def chat_with_mneme(
    message: str,
    history: List[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str]], str]:
    """
    Send message to Mneme and get response.

    Args:
        message: User message
        history: Chat history

    Returns:
        Updated history and empty string for input
    """
    global conversation_id

    if not message.strip():
        return history, ""

    try:
        # Call Mneme API
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "conversation_id": conversation_id,
                "include_sources": True,
                "max_sources": 5
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        # Update conversation ID
        if data.get("conversation_id"):
            conversation_id = data["conversation_id"]

        # Format response with sources
        assistant_message = data["message"]

        if data.get("sources"):
            assistant_message += "\n\n**📚 Fonti:**\n"
            for i, source in enumerate(data["sources"], 1):
                file_name = source.get("file_path", "Unknown").split("/")[-1]
                score = source.get("score", 0) * 100
                assistant_message += f"\n{i}. **{file_name}** (rilevanza: {score:.1f}%)"

        # Add stats
        if data.get("processing_time_ms"):
            time_ms = data["processing_time_ms"]
            assistant_message += f"\n\n*⏱️ Tempo: {time_ms:.0f}ms*"

        # Update history
        history.append((message, assistant_message))

        return history, ""

    except requests.exceptions.ConnectionError:
        error_msg = "❌ **Errore di connessione**\n\nAssicurati che Mneme sia in esecuzione:\n```bash\ndocker compose up -d\n```"
        history.append((message, error_msg))
        return history, ""

    except requests.exceptions.Timeout:
        error_msg = "⏰ **Timeout**\n\nLa richiesta ha impiegato troppo tempo."
        history.append((message, error_msg))
        return history, ""

    except Exception as e:
        error_msg = f"❌ **Errore**: {str(e)}"
        history.append((message, error_msg))
        return history, ""


def get_health_status() -> str:
    """Get Mneme health status with retry logic."""
    import time

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            response.raise_for_status()
            data = response.json()

            status = data.get("status", "unknown")
            docs = data.get("vector_store_documents", 0)
            provider = data.get("llm_provider", "unknown")

            if status == "healthy":
                return f"✅ **Mneme è attivo**\n\n📊 {docs} chunks nel vector store\n🤖 Provider: {provider}"
            else:
                return f"⚠️ Status: {status}"

        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return f"❌ Mneme non è raggiungibile\n\nAssicurati che l'API sia in esecuzione su:\n{API_BASE_URL}"
        except Exception as e:
            return f"❌ Errore: {str(e)}"

    return "❌ Impossibile connettersi all'API"


def clear_conversation() -> Tuple[List, str]:
    """Clear conversation history."""
    global conversation_id
    conversation_id = None
    return [], "Conversazione resettata! 🔄"


# Create Gradio interface
with gr.Blocks(
    title="Mneme Chat",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="indigo"
    )
) as demo:

    gr.Markdown(
        """
        # 🧠 Mneme Chat
        ### Chatta con le tue note Obsidian

        Fai domande sulle tue note e ricevi risposte basate sul contenuto del tuo vault.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Conversazione",
                height=500,
                show_label=False,
                avatar_images=(
                    None,  # User avatar
                    "https://em-content.zobj.net/thumbs/240/apple/354/brain_1f9e0.png"  # Assistant avatar
                )
            )

            with gr.Row():
                msg = gr.Textbox(
                    label="Messaggio",
                    placeholder="Scrivi la tua domanda qui... (premi Invio per inviare)",
                    show_label=False,
                    scale=4
                )
                send_btn = gr.Button("Invia 📤", scale=1, variant="primary")

            with gr.Row():
                clear_btn = gr.Button("🔄 Nuova conversazione", size="sm")

        with gr.Column(scale=1):
            gr.Markdown("### ℹ️ Info")
            status_box = gr.Markdown(
                get_health_status(),
                label="Status"
            )
            refresh_btn = gr.Button("🔄 Aggiorna Status", size="sm")

            gr.Markdown("### 💡 Esempi di domande")
            gr.Examples(
                examples=[
                    "Cosa ho scritto su AI e machine learning?",
                    "Riassumimi i miei progetti",
                    "Parlami delle mie note su AWS",
                    "Cosa c'è nelle mie note su Python?",
                    "Quali sono i miei obiettivi?",
                ],
                inputs=msg
            )

    gr.Markdown(
        """
        ---
        **Suggerimenti:**
        - Fai domande specifiche per risultati migliori
        - Le fonti mostrano da quali note provengono le risposte
        - La rilevanza indica quanto è pertinente la fonte (0-100%)
        """
    )

    # Event handlers
    msg.submit(
        fn=chat_with_mneme,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )

    send_btn.click(
        fn=chat_with_mneme,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )

    clear_btn.click(
        fn=clear_conversation,
        outputs=[chatbot, status_box]
    )

    refresh_btn.click(
        fn=get_health_status,
        outputs=status_box
    )


def main():
    """Main entry point for Gradio chat interface."""
    print("🚀 Avvio Gradio Chat Interface...")
    print(f"📡 Connessione a Mneme API: {API_BASE_URL}")
    print("\n" + get_health_status())
    print("\n🌐 Aprendo l'interfaccia web...")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False
    )


if __name__ == "__main__":
    main()

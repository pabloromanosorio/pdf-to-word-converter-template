from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
import vertexai

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from google.cloud import documentai
from vertexai.generative_models import GenerativeModel, Part
from html4docx import HtmlToDocx
from docx import Document

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
REGION = os.environ.get("GOOGLE_CLOUD_REGION")
DOCAI_PROCESSOR_NAME = os.environ.get("DOCAI_PROCESSOR_NAME")

if not PROJECT_ID or not REGION:
    raise ValueError("Missing required environment variables: GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_REGION")

vertexai.init(project=PROJECT_ID, location=REGION)

# --- FastAPI App Setup ---
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# --- Prompts ---
PIPELINE_C_PROMPT = '''
You are a state-of-the-art document conversion engine. Your task is to emulate a multi-stage pipeline to convert the provided document image into a clean, self-contained HTML file.

Your final output must be ONLY the raw HTML code, with no other text or explanations.

You will internally follow these three steps before producing your final answer:

1.  **Internal Step 1: Analyze Layout.** Analyze the image to identify all significant content blocks (e.g., titles, paragraphs, tables, lists). Define the reading order of these blocks.
2.  **Internal Step 2: Transcribe Content.** For each block you identified, transcribe the text within it. You MUST preserve formatting like **bold** and *italic* text. If you see a handwritten signature, transcribe it as `[Signature]`. If you see a seal, transcribe its text and prefix it with `[Seal]`.
3.  **Internal Step 3: Generate and Review Final HTML.** Using your analysis from the previous steps, generate the complete HTML file. **Before you output the code, perform a self-correction pass.** Review your generated HTML against your internal analysis from Steps 1 and 2. Ensure all identified text blocks have been included in the correct reading order and that no content has been hallucinated or misplaced. Adhere to the user\'s special instructions: {user_context}.
'''

PIPELINE_B_PROMPT = '''
You are a programmatic data rendering engine that converts structured JSON into high-fidelity HTML. Your task is to meticulously parse the provided JSON object from Google\'s Document AI Layout Parser and generate a single, self-contained HTML file that visually and structurally replicates the original document.

**Key Instructions:**
1. The full text content is located in the root `text` field.
2. Iterate through each page in the `pages` array.
3. For each page, iterate through its `paragraphs` and `tables` arrays.
4. For Paragraphs: Use the `textAnchor` to extract the text slice from the root `text` field. Use the `layout.boundingPoly` coordinates to create an absolutely positioned `<div>` in the HTML containing that text.
5. For Tables: For each `table` object, iterate through its `headerRows` and `bodyRows`. For each cell, use its `textAnchor` to get the content. You MUST use the cell\'s `rowSpan` and `colSpan` properties to generate the correct `rowspan` and `colspan` attributes in the final HTML `<td>` elements.
6. For Styles: As you process each text segment, check for associated styles and apply them using `<strong>`, `<em>` tags or inline CSS.
7. The text content is from OCR; if you encounter obvious typographical errors given the context (e.g., 'Universty'), correct them in your HTML output.
8. Adhere to the user\'s special instructions: {user_context}.
9. Your final output must be ONLY the raw HTML code.
'''

@app.get("/")
def read_root(request: Request):
    """Serves the initial HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    model_choice: str = Form("gemini-2.5-flash"),
    user_context: str = Form("No special instructions provided."),
    pipeline_choice: str = Form("C")
):
    """Handles file upload, AI processing, and DOCX conversion."""

    html_content = ""

    if pipeline_choice == 'C':
        # --- PIPELINE C LOGIC ---
        image_part = Part.from_data(mime_type=file.content_type, data=await file.read())
        prompt = PIPELINE_C_PROMPT.format(user_context=user_context)
        model = GenerativeModel(model_choice)
        response = await model.generate_content_async([image_part, prompt])
        html_content = response.text

    else: # Pipeline B
        # --- PIPELINE B LOGIC ---
        if not DOCAI_PROCESSOR_NAME:
            raise ValueError("Missing required environment variable for Pipeline B: DOCAI_PROCESSOR_NAME")
        
        docai_client = documentai.DocumentProcessorServiceClient()
        await file.seek(0)
        file_data = await file.read()
        
        raw_document = documentai.RawDocument(content=file_data, mime_type=file.content_type)
        request = documentai.ProcessRequest(name=DOCAI_PROCESSOR_NAME, raw_document=raw_document)
        result = docai_client.process_document(request=request)
        
        doc_ai_json = documentai.Document.to_json(result.document)

        prompt = PIPELINE_B_PROMPT.format(user_context=user_context)
        model = GenerativeModel(model_choice)
        response = await model.generate_content_async([prompt, doc_ai_json])
        html_content = response.text

    # Common steps for both pipelines
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0]

    # Convert HTML to DOCX
    parser = HtmlToDocx()
    document = Document()
    parser.add_html_to_document(html_content, document)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
        document.save(temp_docx)
        temp_docx_path = temp_docx.name

    # Return the DOCX file as a download
    return FileResponse(
        path=temp_docx_path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=f"{os.path.splitext(file.filename)[0]}_converted.docx",
        background=BackgroundTask(lambda: os.remove(temp_docx_path))
    )
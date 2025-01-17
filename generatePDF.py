import random
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as PDFImage
from reportlab.lib.styles import getSampleStyleSheet
import os
from PIL import Image as PILImage

pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.readlines()


def select_random_items(items, count):
    return random.sample(items, min(len(items), count))

from reportlab.lib.enums import TA_CENTER

def generate_pdf(filepath, content, images=None):
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "DejaVuSans"
    styles["Normal"].fontSize = 12

    heading_style = styles["Heading2"]
    heading_style.fontName = "DejaVuSans-Bold"
    heading_style.fontSize = 14
    heading_style.alignment = TA_CENTER

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []

    question_number = 1
    for topic_name, topic_content in content.items():
        if not topic_content: continue
        elements.append(Paragraph(topic_name, heading_style))

        for line in topic_content:
            if isinstance(line, str):
                paragraph = Paragraph(f"{question_number}. {line.strip()}", styles["Normal"])
                elements.append(paragraph)
            elif isinstance(line, tuple):
                image_path, description = line
                if os.path.exists(image_path):
                    img = PILImage.open(image_path)
                    img.save(image_path)
                    elements.append(Paragraph(f"{question_number}. {description}", styles["Normal"]))
                    elements.append(Spacer(1, 9))
                    elements.append(PDFImage(image_path))
                else:
                    elements.append(Paragraph(f"{question_number}. {description}", styles["Normal"]))
            elements.append(Spacer(1, 12))
            question_number += 1

    doc.build(elements)

def generate_work(questions_per_topic, num_variants):
    base_folders = {
        "definitions": "Определения",
        "formulas": "Формулы",
        "definitions_answers": "Определения ответы",
        "formulas_answers": "Формулы ответы",
    }

    topics = os.listdir(base_folders["definitions"])

    output_folder = f"Вывод {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    os.makedirs(output_folder, exist_ok=True)

    for variant in range(1, num_variants + 1):
        questions = {}
        answers = {}

        for topic_index, topic in enumerate(topics):
            topic_name = topic.replace('.txt', '')

            questions[topic_name] = []
            answers[topic_name] = []

            definitions_path = os.path.join(base_folders["definitions"], topic)
            definitions = read_file(definitions_path)
            selected_definitions = select_random_items(definitions, questions_per_topic[topic_index][1])
            for q in selected_definitions:
                questions[topic_name].append(q.strip())
                definitions_answers_path = os.path.join(base_folders["definitions_answers"], topic)
                definitions_answers = read_file(definitions_answers_path)
                answer = definitions_answers[definitions.index(q)].strip()
                answers[topic_name].append(f"Определение: {answer}")

            formulas_path = os.path.join(base_folders["formulas"], topic)
            formulas = read_file(formulas_path)
            selected_formulas = select_random_items(formulas, questions_per_topic[topic_index][0])
            for q in selected_formulas:
                questions[topic_name].append(q.strip())
                formulas_answers_folder = os.path.join(base_folders["formulas_answers"], topic_name)
                answer_image = os.path.join(formulas_answers_folder, f"{formulas.index(q) + 1}.png")
                if os.path.exists(answer_image):
                    answers[topic_name].append((answer_image, f"Формула: {q.strip()}"))
                else:
                    answers[topic_name].append(f"[Изображение отсутствует для формулы: {q.strip()}]")

        questions_file = os.path.join(output_folder, f"Вариант {variant}.pdf")
        answers_file = os.path.join(output_folder, f"Вариант {variant} ответы.pdf")

        generate_pdf(questions_file, questions)
        generate_pdf(answers_file, answers)

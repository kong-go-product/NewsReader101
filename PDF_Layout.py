from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
# Register the correct path for the NotoSansSC font supporting Chinese characters
pdfmetrics.registerFont(TTFont('NotoSansSC',r'C:\eNews\Noto_Sans_SC\static\NotoSansSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSansSC-SemiBold', r'C:\eNews\Noto_Sans_SC\static\NotoSansSC-SemiBold.ttf'))

# A2 dimensions in landscape mode  
PAGE_WIDTH, PAGE_HEIGHT = landscape(A3)

# Number of columns and layout settings
NUM_COLUMNS = 4  # Narrower columns for compact layout
COLUMN_SPACING = 0.3 * inch  # Reduced column spacing
LEFT_MARGIN = 0.5 * inch
RIGHT_MARGIN = 0.5 * inch
TOP_MARGIN = 1.5 * inch
BOTTOM_MARGIN = 1 * inch
LINE_SPACING = 16.8  # Adjust as needed for 
TITLE_NAME = 'NotoSansSC-SemiBold'
BODY_NAME = 'NotoSansSC'
FONT_SIZE_TITLE = 14
FONT_SIZE_BODY = 12

# Function to read content from a .txt file
def read_txt_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        # lines = file.readlines()
        # if not lines: 
        #     return "Untitled", ""  # Default title if file is empty
        # headline = lines[0].strip()
        body_text = ''.join(file.readlines()).strip()
    # return headline, body_text
    return body_text  

# Function to calculate text width with a specific font and size
def get_text_width(text, font, font_size):
    return pdfmetrics.stringWidth(text, font, font_size)

# Enhanced wrap_text function with improved word boundary handling
def wrap_text(text, column_width, font, font_size):
    lines = []
    current_line = ''
    current_width = 0

    for char in text:
        # Handle new lines in source text
        if char == '\n':
            lines.append(current_line)
            current_line = ''
            current_width = 0
            continue

        char_width = get_text_width(char, font, font_size)

        # Check if adding this character exceeds column width
        if current_width + char_width > column_width:
            if current_line:  # If there's content, add to lines
                lines.append(current_line)
            current_line = char
            current_width = char_width
        else:
            current_line += char
            current_width += char_width

    if current_line:  # Add any remaining text as a line
        lines.append(current_line)

    return lines

# Function to draw text in continuous columns
def draw_in_columns(c, text_blocks, start_x, start_y, column_width, column_index):
    y = start_y
    for font, size, lines in text_blocks:
        c.setFont(font, size)
        for line in lines:
            if y < BOTTOM_MARGIN + LINE_SPACING:
                column_index += 1
                if column_index >= NUM_COLUMNS:  # Move to a new page if all columns are used
                    c.showPage()
                    c.setFont(font, size)  # Reset font on new page
                    column_index = 0
                    y = PAGE_HEIGHT - TOP_MARGIN
                else:
                    y = PAGE_HEIGHT - TOP_MARGIN  # Reset y for a new column

            x = start_x + (column_index * (column_width + COLUMN_SPACING))
            c.drawString(x, y, line)
            y -= LINE_SPACING  # Move down by line spacing

        # Add extra spacing after each block of text
        y -= LINE_SPACING  # Space after each block of text

    return y, column_index  # Return last y position and column index

# Function to create the PDF with continuous columns
def create_pdf(filename, articles):
    c = canvas.Canvas(filename, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    column_width = (PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - (NUM_COLUMNS - 1) * COLUMN_SPACING) / NUM_COLUMNS
    start_x = LEFT_MARGIN
    start_y = PAGE_HEIGHT - TOP_MARGIN
    column_index = 0

    # Draw articles in columns
    for body in articles:
        # Split the body into lines for processing
        for line in body.split('\n'):
            if line.startswith('**') and line.endswith('**'):  # Check for bold text in Markdown
                text = line.strip('**')  # Remove ** from start and end
                wrapped_body = wrap_text(text, column_width, TITLE_NAME, FONT_SIZE_BODY)  # Bold font
                text_blocks = [(TITLE_NAME, FONT_SIZE_BODY, wrapped_body)]
            else:
                wrapped_body = wrap_text(line, column_width, BODY_NAME, FONT_SIZE_BODY)  # Normal body text
                text_blocks = [(BODY_NAME, FONT_SIZE_BODY, wrapped_body)]

            # Draw text in continuous columns
            start_y, column_index = draw_in_columns(c, text_blocks, start_x, start_y, column_width, column_index)
            start_y -= LINE_SPACING * 0 # Space after each line

    c.save()

# Paths to .txt files
txt_files = ['merged_articles.txt']

# Read and format articles
articles = [read_txt_file(file) for file in txt_files]

# Create the PDF
create_pdf(f"news_{datetime.now().strftime('%Y-%m-%d')}.pdf", articles)

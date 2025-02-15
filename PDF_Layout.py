from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime

class PDFLayout:
    def __init__(self, output_filename, txt_files):
        self.output_filename = output_filename
        self.txt_files = txt_files

        # Register the fonts
        pdfmetrics.registerFont(TTFont('NotoSansSC', r'C:\eNews\Noto_Sans_SC\static\NotoSansSC-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('NotoSansSC-SemiBold', r'C:\eNews\Noto_Sans_SC\static\NotoSansSC-SemiBold.ttf'))

        # A2 dimensions in landscape mode  
        self.PAGE_WIDTH, self.PAGE_HEIGHT = landscape(A3)

        # Layout settings
        self.NUM_COLUMNS = 4
        self.COLUMN_SPACING = 0.3 * inch
        self.LEFT_MARGIN = 0.5 * inch
        self.RIGHT_MARGIN = 0.5 * inch
        self.TOP_MARGIN = 1.5 * inch
        self.BOTTOM_MARGIN = 1 * inch
        self.LINE_SPACING = 16.8
        self.TITLE_NAME = 'NotoSansSC-SemiBold'
        self.BODY_NAME = 'NotoSansSC'
        self.FONT_SIZE_TITLE = 14
        self.FONT_SIZE_BODY = 12

    def read_txt_file(self, filepath):
        """Function to read content from a .txt file"""
        with open(filepath, 'r', encoding='utf-8') as file:
            body_text = ''.join(file.readlines()).strip()
        return body_text

    def get_text_width(self, text, font, font_size):
        """Function to calculate text width with a specific font and size"""
        return pdfmetrics.stringWidth(text, font, font_size)

    def wrap_text(self, text, column_width, font, font_size):
        """Enhanced wrap_text function with improved word boundary handling"""
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

            char_width = self.get_text_width(char, font, font_size)

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

    def draw_in_columns(self, c, text_blocks, start_x, start_y, column_width, column_index):
        """Function to draw text in continuous columns"""
        y = start_y
        for font, size, lines in text_blocks:
            c.setFont(font, size)
            for line in lines:
                if y < self.BOTTOM_MARGIN + self.LINE_SPACING:
                    column_index += 1
                    if column_index >= self.NUM_COLUMNS:  # Move to a new page if all columns are used
                        c.showPage()
                        c.setFont(font, size)  # Reset font on new page
                        column_index = 0
                        y = self.PAGE_HEIGHT - self.TOP_MARGIN
                    else:
                        y = self.PAGE_HEIGHT - self.TOP_MARGIN  # Reset y for a new column

                x = start_x + (column_index * (column_width + self.COLUMN_SPACING))
                c.drawString(x, y, line)
                y -= self.LINE_SPACING  # Move down by line spacing

            # Add extra spacing after each block of text
            y -= self.LINE_SPACING  # Space after each block of text

        return y, column_index  # Return last y position and column index

    def create_pdf(self):
        """Function to create the PDF with continuous columns"""
        c = canvas.Canvas(self.output_filename, pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        column_width = (self.PAGE_WIDTH - self.LEFT_MARGIN - self.RIGHT_MARGIN - (self.NUM_COLUMNS - 1) * self.COLUMN_SPACING) / self.NUM_COLUMNS
        start_x = self.LEFT_MARGIN
        start_y = self.PAGE_HEIGHT - self.TOP_MARGIN
        column_index = 0

        # Read and format articles
        articles = [self.read_txt_file(file) for file in self.txt_files]

        # Draw articles in columns
        for body in articles:
            # Split the body into lines for processing
            for line in body.split('\n'):
                if line.startswith('**') and line.endswith('**'):  # Check for bold text in Markdown
                    text = line.strip('**')  # Remove ** from start and end
                    wrapped_body = self.wrap_text(text, column_width, self.TITLE_NAME, self.FONT_SIZE_BODY)  # Bold font
                    text_blocks = [(self.TITLE_NAME, self.FONT_SIZE_BODY, wrapped_body)]
                else:
                    wrapped_body = self.wrap_text(line, column_width, self.BODY_NAME, self.FONT_SIZE_BODY)  # Normal body text
                    text_blocks = [(self.BODY_NAME, self.FONT_SIZE_BODY, wrapped_body)]

                # Draw text in continuous columns
                start_y, column_index = self.draw_in_columns(c, text_blocks, start_x, start_y, column_width, column_index)
                start_y -= self.LINE_SPACING * 0  # Space after each line

        c.save()


# Example usage:
if __name__ == '__main__':
    txt_files = ['merged_articles.txt']
    output_filename = f"news_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    pdf_layout = PDFLayout(output_filename, txt_files)
    pdf_layout.create_pdf()

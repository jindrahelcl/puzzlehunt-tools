#!/usr/bin/env python3

# Based on output generated by chatgpt

import math

def gen_line(*args):
    commands = []
    points = iter(args)
    point = next(points)
    commands.append(f"{point[0]:.4f} {point[1]:.4f} m")
    for point in points:
        commands.append(f"{point[0]:.4f} {point[1]:.4f} l")
    commands.append("S")  # Stroke the line
    return commands

# Function to generate PDF commands for a hexagon
def gen_hexagon(x_center, y_center, size):
    points = []
    for i in range(4):  # Draw only three sides of the hexagon
        angle = math.radians(i * 60)
        x = x_center + size * math.sin(angle)
        y = y_center + size * math.cos(angle)
        points.append([x, y])
    return gen_line(*points)

# Function to generate PDF syntax for the hexagonal grid
def gen_hex_grid(radius, size, width, height):
    hex_centers = []
    commands = []
    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)
        hex_centers_line = []
        for r in range(r1, r2 + 1):
            x = width / 2 + size * (math.sqrt(3) * (r + q / 2))
            y = height / 2 + size * (3/2 * q)
            hex_centers_line.append((x, y))
            commands.extend(gen_hexagon(x, y, size))
        hex_centers.append(hex_centers_line)
    return commands, hex_centers

# Function to generate PDF syntax for the triangular dual grid
def gen_triangular_dual(hex_centers, radius):
    commands = []

    for line in hex_centers:
        commands.extend(gen_line(line[0], line[-1]))

    for i in range(radius):
        commands.extend(gen_line(hex_centers[0][i], hex_centers[-1-i][-1]))

    for i in range(1, radius):
        commands.extend(gen_line(hex_centers[i][0], hex_centers[-1][-1-i]))

    for i in range(radius):
        commands.extend(gen_line(hex_centers[0][-1-i], hex_centers[-1-i][0]))

    for i in range(1, radius):
        commands.extend(gen_line(hex_centers[i][-1], hex_centers[-1][i]))

    return commands

def gen_bleed(width, height, bleed, mark):
    commands = []

    commands.extend(gen_line([0, -bleed-mark], [0, -bleed]))
    commands.extend(gen_line([-bleed-mark, 0], [-bleed, 0]))
    commands.extend(gen_line([-bleed, -bleed-mark], [-bleed, -bleed], [-bleed-mark, -bleed]))

    commands.extend(gen_line([width, -bleed-mark], [width, -bleed]))
    commands.extend(gen_line([width+bleed+mark, 0], [width+bleed, 0]))
    commands.extend(gen_line([width+bleed, -bleed-mark], [width+bleed, -bleed], [width+bleed+mark, -bleed]))

    commands.extend(gen_line([width, height+bleed+mark], [width, height+bleed]))
    commands.extend(gen_line([width+bleed+mark, height], [width+bleed, height]))
    commands.extend(gen_line([width+bleed, height+bleed+mark], [width+bleed, height+bleed], [width+bleed+mark, height+bleed]))

    commands.extend(gen_line([0, height+bleed+mark], [0, height+bleed]))
    commands.extend(gen_line([-bleed-mark, height], [-bleed, height]))
    commands.extend(gen_line([-bleed, height+bleed+mark], [-bleed, height+bleed], [-bleed-mark, height+bleed]))

    return commands

def gen_content_stream(radius, size, width, height, bleed, mark):
    content_stream = []
    content_stream.append(".92 G")  # Set stroke color
    content_stream.append("2 w")  # Set line width

    # Generate hexagons and dual grid lines
    hex_commands, hex_centers = gen_hex_grid(radius, size, width, height)
    content_stream.extend(hex_commands)

    content_stream.append(".7 G")  # Set stroke color
    content_stream.append(".5 w")  # Set line width
    content_stream.append("[.5 1 .5 1 .5 1 .5 1 .5 1 .5 1 0 0.5 0 1 .5 1 .5 1 .5 1 .5 1 .5 1] .25 d")  # Set dash pattern
    dual_commands = gen_triangular_dual(hex_centers, radius)
    content_stream.extend(dual_commands)

    content_stream.append("0 G")  # Set stroke color
    content_stream.append("1 w")  # Set line width
    content_stream.append("[] 0 d")  # Set dash pattern
    bleed_commands = gen_bleed(width, height, bleed, mark)
    content_stream.extend(bleed_commands)

    return "\n".join(content_stream)

# Main function to generate the entire PDF content
def gen_pdf(radius, size, width, height, bleed, mark):
    pdf_content = []

    # PDF header and object declarations
    pdf_content.append("%PDF-1.4")
    offset = sum(len(line) + 1 for line in pdf_content)
    objects = []
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    objects.append("2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] /Resources << >> >>\nendobj")
    objects.append(f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [{-bleed-mark} {-bleed-mark} {width+bleed+mark} {height+bleed+mark}] /CropBox [0 0 {width} {height}] /BleedBox [{-bleed} {-bleed} {width+bleed} {height+bleed}] /Contents 4 0 R >>\nendobj")
    #objects.append(f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [{-bleed-mark-9} {-bleed-mark-9} {width+bleed+mark+9} {height+bleed+mark+9}] /Contents 4 0 R >>\nendobj")

    # Content stream
    content_stream = gen_content_stream(radius, size, width, height, bleed, mark)
    content_stream_object = []
    content_stream_object.append(f"4 0 obj\n<< /Length {len(content_stream)} >> stream")
    content_stream_object.append(content_stream)
    content_stream_object.append("endstream\nendobj")
    objects.append("\n".join(content_stream_object))

    pdf_content.extend(objects)

    # Cross-reference table
    pdf_content.append("xref")
    pdf_content.append(f"0 {len(objects) + 1}")
    pdf_content.append("0000000000 65535 f ")
    for obj in objects:
        pdf_content.append(f"{offset:010} 00000 n ")
        offset += len(obj) + 1

    # Trailer and EOF
    pdf_content.append(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>")
    pdf_content.append("startxref")
    pdf_content.append(str(offset))
    pdf_content.append("%%EOF")

    return "\n".join(pdf_content) + "\n"

# Parameters
hex_radius = 31  # Number of hexagons from center to edge in grid
hex_size = 6*math.sqrt(3)   # Size of each hexagon
page_width = 595  # Page width in points (8.5 inches)
page_height = 842  # Page height in points (11 inches)
bleed = 9
mark = 18

# Generate the PDF content
pdf_content = gen_pdf(hex_radius, hex_size, page_width, page_height, bleed, mark)

# Save to a file
with open("trihex.pdf", "w") as f:
    f.write(pdf_content)

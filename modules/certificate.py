import datetime
import base64
import os
from .data_manager import LOGO_PATH

def create_certificate(name, score, date, cert_id=None):
    """
    Generate an enhanced HTML certificate with improved design
    
    Args:
        name (str): Name of the recipient
        score (str): Score percentage
        date (str): Date of completion
        cert_id (str, optional): Unique certificate ID
    
    Returns:
        str: HTML content of the certificate
    """
    # Generate a certificate ID if not provided
    if not cert_id:
        import hashlib
        cert_id = hashlib.md5(f"{name}_{score}_{date}".encode()).hexdigest()[:8].upper()
    
    # Check if we have a company logo
    if os.path.exists(LOGO_PATH):
        # Encode logo to base64 for embedding in HTML
        with open(LOGO_PATH, "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
        logo_embed = f"data:image/png;base64,{logo_base64}"
    else:
        # Use placeholder if no logo
        logo_embed = "https://via.placeholder.com/150x100?text=COMPANY+LOGO"
    
    # Creating an enhanced certificate with better design
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Forklift Operator Certificate</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Montserrat', sans-serif;
                background-color: #f5f5f5;
                color: #333;
                padding: 20px;
            }}
            
            .certificate-container {{
                width: 850px;
                position: relative;
                margin: 0 auto;
                background-color: #fff;
                overflow: hidden;
            }}
            
            .certificate {{
                border: 20px solid transparent;
                border-image: linear-gradient(45deg, #1E88E5, #0D47A1) 1;
                padding: 40px;
                position: relative;
                background-color: #fff;
                z-index: 2;
            }}
            
            .watermark {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url('{logo_embed}');
                background-repeat: no-repeat;
                background-position: center;
                background-size: 60%;
                opacity: 0.05;
                z-index: 1;
                pointer-events: none;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #eaeaea;
            }}
            
            .logo {{
                max-height: 80px;
            }}
            
            .certificate-id {{
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
                color: #888;
                text-align: right;
            }}
            
            .certificate-title {{
                text-align: center;
                margin: 20px 0 40px;
            }}
            
            .certificate-heading {{
                font-family: 'Playfair Display', serif;
                font-size: 48px;
                color: #1E88E5;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            
            .certificate-subheading {{
                font-size: 22px;
                color: #555;
                font-weight: 600;
            }}
            
            .recipient-section {{
                text-align: center;
                margin: 40px 0;
            }}
            
            .presented-to {{
                font-size: 16px;
                color: #666;
                margin-bottom: 15px;
            }}
            
            .recipient-name {{
                font-family: 'Playfair Display', serif;
                font-size: 36px;
                color: #333;
                position: relative;
                display: inline-block;
                padding: 0 20px 10px;
            }}
            
            .recipient-name::after {{
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 1px;
                background: linear-gradient(to right, transparent, #1E88E5, transparent);
            }}
            
            .achievement {{
                margin: 40px 0;
                text-align: center;
                font-size: 18px;
                line-height: 1.6;
                color: #555;
            }}
            
            .score {{
                font-weight: 700;
                color: #1E88E5;
                font-size: 26px;
                margin: 10px 0;
                display: block;
            }}
            
            .date-section {{
                text-align: center;
                margin: 30px 0;
                font-size: 16px;
                color: #666;
            }}
            
            .date {{
                font-weight: 600;
                color: #333;
            }}
            
            .signature-section {{
                display: flex;
                justify-content: space-between;
                margin-top: 60px;
            }}
            
            .signature {{
                text-align: center;
                width: 45%;
            }}
            
            .signature-line {{
                width: 80%;
                height: 1px;
                background-color: #333;
                margin: 10px auto;
            }}
            
            .signature-name {{
                font-weight: 600;
                font-size: 16px;
            }}
            
            .signature-title {{
                font-size: 14px;
                color: #666;
            }}
            
            .footer {{
                margin-top: 40px;
                font-size: 12px;
                color: #888;
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #eaeaea;
            }}
            
            .validity {{
                margin-top: 10px;
                font-style: italic;
            }}
            
            .verification {{
                margin-top: 5px;
                font-weight: 600;
            }}
            
            @media print {{
                body {{
                    background-color: white;
                    padding: 0;
                }}
                
                .certificate-container {{
                    width: 100%;
                    box-shadow: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="certificate-container">
            <div class="certificate">
                <div class="watermark"></div>
                
                <div class="header">
                    <img src="{logo_embed}" alt="Company Logo" class="logo">
                    <div class="certificate-id">
                        Certificate ID: {cert_id}<br>
                        Issue Date: {date}
                    </div>
                </div>
                
                <div class="certificate-title">
                    <h1 class="certificate-heading">Certificate</h1>
                    <h2 class="certificate-subheading">of Achievement</h2>
                </div>
                
                <div class="recipient-section">
                    <p class="presented-to">This certifies that</p>
                    <h3 class="recipient-name">{name}</h3>
                </div>
                
                <div class="achievement">
                    has successfully completed the<br>
                    <strong>Forklift Operator Safety Training</strong><br>
                    demonstrating proficiency in safety protocols and operational procedures<br>
                    with a score of<br>
                    <span class="score">{score}%</span>
                </div>
                
                <div class="date-section">
                    Completed on <span class="date">{date}</span>
                </div>
                
                <div class="signature-section">
                    <div class="signature">
                        <div class="signature-line"></div>
                        <p class="signature-name">Operations Manager</p>
                        <p class="signature-title">Certification Authority</p>
                    </div>
                    
                    <div class="signature">
                        <div class="signature-line"></div>
                        <p class="signature-name">Training Director</p>
                        <p class="signature-title">Safety Department</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This certificate validates that the recipient has demonstrated knowledge of forklift safety procedures 
                    and is qualified in accordance with OSHA standards for the operation of forklifts.</p>
                    <p class="validity">Valid for one year from the date of issue.</p>
                    <p class="verification">Verify certificate authenticity with Certificate ID: {cert_id}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
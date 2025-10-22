import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

from back.src.excepciones import ErrorEnvioCorreo
from back.src.modelos.inscripcion import Inscripcion

class ServicioCorreo:
    """Clase responsable de enviar comprobante usando SMTP"""
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self, remitente: str, password_app: str):
        self.remitente = remitente
        self.password_app = password_app

        # ... (ServicioCorreo class code before generar_html_comprobante) ...

    def generar_html_comprobante(self, inscripcion, email_contacto):
        """
        Genera el cuerpo HTML del comprobante con estilo visual usando la paleta verde.
        """
        # --- CORRECCIÓN CLAVE: Usar inscripcion.turno.atributo ---
        participantes_html = "".join([
            f"<li>{v.nombre} (DNI: {v.dni}, Edad: {v.edad}{' - Talle ' + v.talle if v.talle else ''})</li>"
            for v in inscripcion.visitantes
            # NOTA: Usar 'visitantes' si es el nombre correcto del atributo en Inscripcion
        ])

        # Acceso a los atributos de Turno:
        actividad_nombre = inscripcion.turno.actividad_nombre  # Accede al nombre de la actividad
        fecha_str = inscripcion.turno.fecha.strftime('%d/%m/%Y')  # Formato de fecha
        hora_str = inscripcion.turno.hora.strftime('%H:%M')  # Formato de hora

        # Se requiere acceso al DNI y Talle de los visitantes
        # Se requiere acceso a la lista de visitantes

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #E8FCCF; padding: 30px; margin: 0;">
            <div style="max-width: 650px; margin: auto; background-color: #ffffff; border-radius: 12px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); overflow: hidden;">

                <div style="background-color: #134611; text-align: center; padding: 20px;">
                    <img src="cid:logo" alt="Logo" style="height: 70px; margin-bottom: 10px;">
                    <h2 style="color: #E8FCCF; margin: 0;">EcoHarmony Park</h2>
                </div>

                <div style="padding: 25px 30px; background-color: #3DA35D; color: white;">
                    <h3 style="text-align: center; margin-top: 0;">🌿 ¡Inscripción Confirmada!</h3>
                    <p style="font-size: 16px;">
                        Tu inscripción fue registrada correctamente. A continuación, encontrarás los detalles del turno:
                    </p>

                    <table style="width: 100%; border-collapse: collapse; background-color: #E8FCCF; color: #134611; border-radius: 8px; margin-top: 15px;">
                        <tr>
                            <td style="padding: 10px;"><strong>Actividad:</strong></td>
                            <td style="padding: 10px;">{actividad_nombre}</td>
                        </tr>
                        <tr style="background-color: #C9F3B3;">
                            <td style="padding: 10px;"><strong>Fecha:</strong></td>
                            <td style="padding: 10px;">{fecha_str}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>Hora:</strong></td>
                            <td style="padding: 10px;">{hora_str}</td>
                        </tr>
                        <tr style="background-color: #C9F3B3;">
                            <td style="padding: 10px;"><strong>Correo de contacto:</strong></td>
                            <td style="padding: 10px;">{email_contacto}</td>
                        </tr>
                    </table>

                    <h4 style="margin-top: 25px; color: #134611;">👥 Participantes:</h4>
                    <ul style="color: #134611; font-size: 15px; background-color: #E8FCCF; border-radius: 8px; padding: 15px; list-style-type: circle;">
                        {participantes_html}
                    </ul>

                    <p style="margin-top: 25px; font-size: 15px; color: #134611;">
                        Te esperamos el día <strong>{fecha_str}</strong> a las <strong>{hora_str}</strong>.
                    </p>
                </div>

                <div style="background-color: #96E072; text-align: center; padding: 15px;">
                    <p style="font-size: 13px; color: #134611; margin: 0;">
                        Este es un mensaje automático, por favor no respondas a este correo.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    def enviar_comprobante(self, inscripcion, email_contacto):
        """
        Envía el comprobante al correo del usuario con formato HTML y logo embebido.
        """
        try:
            mensaje = MIMEMultipart("related")
            mensaje["Subject"] = f"Comprobante de inscripción - {inscripcion.turno.actividad_nombre}"
            mensaje["From"] = self.remitente
            mensaje["To"] = email_contacto

            # Cuerpo HTML del correo
            html = self.generar_html_comprobante(inscripcion, email_contacto)
            mensaje.attach(MIMEText(html, "html"))

            directorio_src = os.path.dirname(os.path.abspath(__file__))
            RUTA_COMPLETA_LOGO = os.path.abspath(
                os.path.join(directorio_src, '..', '..', 'front', 'ecoharmony-ui', 'public', 'logo.png')
            )

            if os.path.exists(RUTA_COMPLETA_LOGO):
                with open(RUTA_COMPLETA_LOGO, "rb") as f:
                    img = MIMEImage(f.read())
                    img.add_header("Content-ID", "<logo>")  # debe coincidir con el cid usado en el HTML
                    img.add_header("Content-Disposition", "inline", filename="logo.png")
                    mensaje.attach(img)
            else:
                print(f"⚠️ No se encontró el logo en {RUTA_COMPLETA_LOGO}")

            # Envío del correo
            with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
                servidor.starttls()
                servidor.login(self.remitente, self.password_app)
                servidor.send_message(mensaje)

            print(f"✅ Correo enviado correctamente a {email_contacto}")

        except Exception as e:
            print(f"⚠️ Error inesperado durante el envío de correo: {e}")

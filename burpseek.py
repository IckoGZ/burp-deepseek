# -*- coding: utf-8 -*-

from burp import (
    IBurpExtender,
    IContextMenuFactory,
    IContextMenuInvocation,
    IHttpRequestResponse,
    IExtensionHelpers,
    ITab,
    IScanIssue
)
from javax.swing import (
    JMenuItem,
    JOptionPane,
    JPanel,
    JLabel,
    JTextField,
    JButton
)
from java.awt import GridLayout, BorderLayout
import json
import urllib2
import threading  # Para crear el hilo en segundo plano

def to_unicode(obj, encoding='utf-8'):
    """
    Convierte un string a 'unicode' en Jython/Python 2.
    Evita errores de codificación ASCII cuando hay caracteres especiales.
    """
    if obj is None:
        return u''
    if isinstance(obj, unicode):
        return obj
    try:
        return obj.decode(encoding)
    except:
        return obj.decode(encoding, 'replace')

class CustomScanIssue(IScanIssue):
    """
    Clase que implementa IScanIssue para reportar hallazgos personalizados
    en Burp. Evita depender de createScanIssue(...) que no existe en Community.
    """
    def __init__(self, http_service, url, http_messages, issue_name, issue_detail, severity):
        self._http_service = http_service
        self._url = url
        self._http_messages = http_messages  # lista/array de IHttpRequestResponse
        self._issue_name = issue_name
        self._issue_detail = issue_detail
        self._severity = severity

    def getUrl(self):
        return self._url

    def getIssueName(self):
        return self._issue_name

    def getIssueType(self):
        # Puedes devolver un número único para tu tipo de issue o usar 0
        # https://portswigger.net/burp/extender/api/constant-values
        return 0

    def getSeverity(self):
        # "High", "Medium", "Low", "Information"
        return self._severity

    def getConfidence(self):
        # "Certain", "Firm" o "Tentative"
        return "Certain"

    def getIssueBackground(self):
        return None

    def getRemediationBackground(self):
        return None

    def getIssueDetail(self):
        # Aquí va el texto principal que se mostrará en el panel de detalles del Issue
        return self._issue_detail

    def getRemediationDetail(self):
        return None

    def getHttpMessages(self):
        return self._http_messages

    def getHttpService(self):
        return self._http_service


class BurpExtender(IBurpExtender, IContextMenuFactory, ITab):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("DeepSeek Analyzer")

        # Registramos el menú contextual y la pestaña
        self._callbacks.registerContextMenuFactory(self)
        self._callbacks.addSuiteTab(self)

        # Configuración por defecto
        self.api_key = ""
        self.default_prompt = (
            "Analyze this HTTP request/response focusing ONLY on potential vulnerabilities. "
            "Look for suspicious endpoints, possible IDOR, or any exposed secrets like API keys. "
            "Do NOT provide any remediation or mitigation steps."
        )

        # Muestra el diálogo de configuración al cargar
        self.show_config_dialog()

    #
    # Context Menu Factory
    #
    def createMenuItems(self, context_menu):
        menu_list = []
        context_id = context_menu.getInvocationContext()

        # Añadimos opciones al menú contextual solo si es request/response
        if context_id in [
            IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_REQUEST,
            IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_RESPONSE,
            IContextMenuInvocation.CONTEXT_MESSAGE_VIEWER_REQUEST,
            IContextMenuInvocation.CONTEXT_MESSAGE_VIEWER_RESPONSE
        ]:
            menu_list.append(
                JMenuItem(
                    "Send to DeepSeek",
                    actionPerformed=lambda event, ctx=context_menu:
                        self.send_to_deepseek(ctx, self.default_prompt)
                )
            )
            menu_list.append(
                JMenuItem(
                    "Send to DeepSeek (custom prompt)",
                    actionPerformed=lambda event, ctx=context_menu:
                        self.send_to_deepseek_custom_prompt(ctx)
                )
            )
        return menu_list if menu_list else None

    #
    # Lógica principal
    #
    def send_to_deepseek(self, context, prompt):
        selected_messages = context.getSelectedMessages()
        if not selected_messages:
            JOptionPane.showMessageDialog(None, "No message selected!")
            return

        message_info = selected_messages[0]  # IHttpRequestResponse
        invocation_id = context.getInvocationContext()

        # Llamamos a la función que hará la petición, en un hilo aparte
        self.send_to_deepseek_async(message_info, invocation_id, prompt)

    def send_to_deepseek_custom_prompt(self, context):
        custom_prompt = JOptionPane.showInputDialog("Enter your custom prompt:")
        if custom_prompt:
            self.send_to_deepseek(context, custom_prompt)

    def send_to_deepseek_async(self, message_info, invocation_id, prompt):
        """
        Lanza la lógica de conexión a DeepSeek en un hilo aparte para no
        bloquear la interfaz de Burp al hacer clic derecho.
        """
        def worker():
            # Aquí dentro hacemos la llamada y creamos el Issue
            self._do_deepseek_request(message_info, invocation_id, prompt)
        t = threading.Thread(target=worker)
        t.start()

    def _do_deepseek_request(self, message_info, invocation_id, prompt):
        """
        Función interna que realmente realiza la llamada a DeepSeek.
        Al estar en un hilo separado, no congela Burp.
        """
        if not self.api_key:
            # Si no hay API Key, abortamos
            return

        # Decidimos si usar request o response según el contexto
        if invocation_id in [
            IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_REQUEST,
            IContextMenuInvocation.CONTEXT_MESSAGE_VIEWER_REQUEST
        ]:
            raw_data = message_info.getRequest()
        else:
            raw_data = message_info.getResponse()

        # Convertimos a unicode seguro
        data_text = to_unicode(self._helpers.bytesToString(raw_data))
        prompt = to_unicode(prompt)
        system_text = to_unicode(
            "You are a specialized cybersecurity auditor focused on bug bounty. "
            "Your ONLY goal is to identify potential vulnerabilities, suspicious endpoints, "
            "possible IDOR, or sensitive data such as exposed API keys or credentials. "
            "Attempt to reconstruct endpoints from partial information. "
            "Do NOT provide any remediation or mitigation steps."
        )

        # Construimos el payload JSON
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": "Bearer {}".format(self.api_key),
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_text},
                {"role": "user",   "content": u"{}\n\n{}".format(prompt, data_text)}
            ],
            "stream": False
        }

        try:
            req_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib2.Request(url, req_data, headers)
            response = urllib2.urlopen(req)
            response_json = json.loads(response.read())

            if "choices" in response_json and len(response_json["choices"]) > 0:
                analysis_text = response_json["choices"][0]["message"]["content"]
            else:
                analysis_text = "No analysis received from DeepSeek."

            # Reemplazamos saltos de línea por <br> para que Burp lo muestre en HTML multilinea
            analysis_text_formatted = analysis_text.replace("\n", "<br>")

            self._create_issue_in_burp(message_info, analysis_text_formatted)

        except Exception as e:
            # Podemos loguear el error en la consola de Extensiones
            print("[DeepSeek Extension] Error: {}".format(str(e)))
            # O mostrarlo en un Popup, pero habría que hacerlo en el hilo de Swing
            # SwingUtilities.invokeLater(lambda: JOptionPane.showMessageDialog(None, ...))

    def _create_issue_in_burp(self, message_info, analysis_html):
        """
        Crea el Issue con severidad 'Information', usando la clase CustomScanIssue.
        """
        request_info = self._helpers.analyzeRequest(message_info)
        url = request_info.getUrl()
        http_service = message_info.getHttpService()

        # Añadimos markers si queremos (aquí None, None)
        self._callbacks.applyMarkers(message_info, None, None)

        issue_name = "DeepSeek Analysis"
        issue_detail = (
            "<b>DeepSeek Analysis</b><br><br>"
            "{}".format(analysis_html)
        )

        new_issue = CustomScanIssue(
            http_service=http_service,
            url=url,
            http_messages=[message_info],
            issue_name=issue_name,
            issue_detail=issue_detail,
            severity="Information"  # Aquí en vez de "High"
        )
        self._callbacks.addScanIssue(new_issue)

    #
    # Configuración (ITab)
    #
    def show_config_dialog(self):
        panel = JPanel(GridLayout(0, 2))
        panel.add(JLabel("API Key:"))
        api_key_field = JTextField(self.api_key, 20)
        panel.add(api_key_field)

        panel.add(JLabel("Default Prompt:"))
        prompt_field = JTextField(self.default_prompt, 20)
        panel.add(prompt_field)

        result = JOptionPane.showConfirmDialog(None, panel, "Configure DeepSeek", JOptionPane.OK_CANCEL_OPTION)
        if result == JOptionPane.OK_OPTION:
            self.api_key = api_key_field.getText()
            self.default_prompt = prompt_field.getText()
            JOptionPane.showMessageDialog(None, "Configuration saved!")

    #
    # Implementación de ITab (pestaña en Burp)
    #
    def getTabCaption(self):
        return "DeepSeek Analyzer"

    def getUiComponent(self):
        panel = JPanel(BorderLayout())
        config_button = JButton("Configure DeepSeek", actionPerformed=lambda x: self.show_config_dialog())
        panel.add(config_button, BorderLayout.NORTH)
        return panel

# Hook de entrada para Burp
if __name__ in ["__main__", "burp"]:
    BurpExtender()

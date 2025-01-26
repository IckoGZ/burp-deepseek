# burp-deepseek
A quick and dirty (and a little shitty) burp extension that uses cheap deepseek api to send request and response and maybe found something interesting.

# DeepSeek Burp Extension

**DeepSeek Burp Extension** is a beta-stage plugin for [PortSwigger Burp Suite](https://portswigger.net/burp) that sends HTTP requests/responses to the [DeepSeek API](https://api.deepseek.com) for AI-driven security analysis. This extension helps bug hunters and security researchers identify potential vulnerabilities, suspicious endpoints, and sensitive data exposures.

> **Disclaimer:** This is a beta version and may contain bugs or incomplete features. Use at your own risk, and always validate any results you get from this extension.

---

## Features

- **Context Menu Integration**  
  Right-click any request/response in Burp (Proxy, Repeater, etc.) to send it to DeepSeek.  

- **Asynchronous Requests**  
  The DeepSeek API call is performed in a separate thread, so Burp remains responsive.  

- **Custom or Default Prompt**  
  Define a default prompt, or enter a custom one for on-the-fly analysis.  

- **Creates Burp Issues**  
  Results are stored as **Information**-level issues in Burp, allowing you to review them later.

---

## How It Works

1. **Select a request/response** in Burp Suite (e.g., in **Proxy** or **Repeater**).  
2. **Right-click** and choose **_Send to DeepSeek_** or **_Send to DeepSeek (custom prompt)_**.  
3. The extension sends the HTTP data to the DeepSeek API for analysis.  
4. Once the API responds, the extension creates a “DeepSeek Analysis” issue in Burp, containing the AI-generated insights.

---

## Requirements

- **Burp Suite** (Community or Professional).  
- **Jython** 2.7+ if you are loading this as a Jython-based extension.  
- A valid **DeepSeek** API key.

---

## Installation

1. **Download or clone** this repository.  
2. In Burp Suite, go to **Extender** > **Extensions**.  
3. Add a new extension:
   - **Extension Type**: Python  
   - **Location**: Select the `burp_deepseek.py` file (or similar) from this repository.  
4. Go to the **DeepSeek Analyzer** tab in Burp to configure your **API Key** and default prompt.  
5. (Optional) Enable **Debug Mode** if you want verbose logs in the Extender console.

---

## Usage

1. **Right-click** on any request or response.  
2. Select **_Send to DeepSeek_** (uses the default prompt) or **_Send to DeepSeek (custom prompt)_**.  
3. The extension will call the DeepSeek API in a separate thread.  
4. When the response comes back, a new **DeepSeek Analysis** issue with severity **Information** appears in **Scanner** > **Issues**.

---

## Contributing

We welcome any contributions or pull requests to improve functionality, fix bugs, or add new features. Feel free to open an issue or submit a PR if you have ideas or encounter any problems.

---

## License

This project is released under the [MIT License](LICENSE).  

---

**Enjoy bug hunting with DeepSeek!**



#TODO
- **Debug Mode**  
  Optionally enable debug logging to see full request/response details in Burp's extender console.  

- **HTML-Formatted Responses**  
  Instruct DeepSeek to return its analysis in HTML for a cleaner readout in Burp’s **Scanner > Issues** panel.  

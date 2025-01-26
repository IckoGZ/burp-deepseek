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

![image](https://github.com/user-attachments/assets/4844b45f-003a-43ce-a65e-e4c0d47071b8)


3. The extension sends the HTTP data to the DeepSeek API for analysis.  
4. Once the API responds, the extension creates a “DeepSeek Analysis” issue in Burp, containing the AI-generated insights.


##Configure 

A prompt will appear when it loads for first time 


After that you can just click hereto reconfigure
![image](https://github.com/user-attachments/assets/af70e918-b636-4449-be81-c460bd118752)


Those are the options
![image](https://github.com/user-attachments/assets/6e54c6b8-59d8-426f-94e0-4e6b7901fef7)


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
4. Go to the **DeepSeek Analyzer** tab in Burp to configure your **API Key** and default prompt.  (Create here the API key https://platform.deepseek.com/api_keys)
5. (Optional) Enable **Debug Mode** if you want verbose logs in the Extender console.

---

## Usage

1. **Right-click** on any request or response.  
2. Select **_Send to DeepSeek_** (uses the default prompt) or **_Send to DeepSeek (custom prompt)_**.  
3. The extension will call the DeepSeek API in a separate thread.  
4. When the response comes back, a new **DeepSeek Analysis** issue with severity **Information** appears in **Scanner** > **Issues**.

---


## Costs

Obviously it depends how much you use :D
Also, the longer the request/response you send to the api, more is going to cost, but in my benchmakrs and tests, 10 requests are 1 cent, so.
1.000 analyzed requests are going to cost about 1 €


![image](https://github.com/user-attachments/assets/bf03ceb6-6048-4c8f-bf5f-6b2ae475d679)

But this is an estimation. Just set up the billing alerts, and top the api with a controlled budget



---

## Contributing

We welcome any contributions or pull requests to improve functionality, fix bugs, or add new features. Feel free to open an issue or submit a PR if you have ideas or encounter any problems.

---

## Modifications

You can just change the endpoints if you want to use chatGPT or another LLM. It is in standard mode.
Also, you can change the default system prompt if you find other system prompot that works better. 

---

## License

This project is released under the [MIT License](LICENSE).  

---

**Enjoy bug hunting with DeepSeek!**


#Issues
Sometimes takes a loooong time to get the response. Don't expect real time
Sometimes it breaks the parser it the input is too long.
Sometimes just it doesn't work



#TODO
- **Debug Mode**  
  Optionally enable debug logging to see full request/response details in Burp's extender console.  

- **HTML-Formatted Responses**  
  Instruct DeepSeek to return its analysis in HTML for a cleaner readout in Burp’s **Scanner > Issues** panel.  

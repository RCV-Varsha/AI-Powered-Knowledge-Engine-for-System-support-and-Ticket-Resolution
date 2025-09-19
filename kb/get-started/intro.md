Extension API
Visual Studio Code is built with extensibility in mind. From the UI to the editing experience, almost every part of VS Code can be customized and enhanced through the Extension API. In fact, many core features of VS Code are built as extensions and use the same Extension API.

This documentation describes:

How to build, run, debug, test, and publish an extension
How to take advantage of VS Code's rich Extension API
Where to find guides and code samples to help get you started
Following our UX guidelines for best practices
Code samples are available at Microsoft/vscode-extension-samples.

If you are looking for published extensions, head to the VS Code Extension Marketplace.

What can extensions do?
Here are some examples of what you can achieve with the Extension API:

Change the look of VS Code with a color or file icon theme - Theming
Add custom components & views in the UI - Extending the Workbench
Create a Webview to display a custom webpage built with HTML/CSS/JS - Webview Guide
Support a new programming language - Language Extensions Overview
Support debugging a specific runtime - Debugger Extension Guide
If you'd like to have a more comprehensive overview of the Extension API, refer to the Extension Capabilities Overview page. Extension Guides Overview also includes a list of code samples and guides that illustrate various Extension API usage.

How to build extensions?
Building a good extension can take a lot of time and effort. Here is what each section of the API docs can help you with:

Get Started teaches fundamental concepts for building extensions with the Hello World sample.
Extension Capabilities dissects VS Code's vast API into smaller categories and points you to more detailed topics.
Extension Guides includes guides and code samples that explain specific usages of VS Code Extension API.
UX Guidelines showcases best practices for providing a great user experience in an extension.
Language Extensions illustrates how to add support for a programming language with guides and code samples.
Testing and Publishing includes in-depth guides on various extension development topics, such as testing and publishing extensions.
Advanced Topics explains advanced concepts such as Extension Host, Supporting Remote Development and GitHub Codespaces, and Proposed API.
References contains exhaustive references for the VS Code API, Contribution Points, and many other topics.
What's new?
VS Code updates on a monthly cadence, and that applies to the Extension API as well. New features and APIs become available every month to increase the power and scope of VS Code extensions.

To stay current with the Extension API, you can review the monthly release notes, which have dedicated sections covering:

Extension authoring - Learn what new extension APIs are available in the latest release.
Proposed extension APIs - Review and give feedback on upcoming proposed APIs.
Looking for help
If you have questions for extension development, try asking on:

VS Code Discussions: GitHub community to discuss VS Code's extension platform, ask questions, help other members of the community, and get answers.
Stack Overflow: There are thousands of questions tagged vscode-extensions, and over half of them already have answers. Search for your issue, ask questions, or help your fellow developers by answering VS Code extension development questions!
VS Code Dev Slack: Public chatroom for extension developers. VS Code team members often join in the conversations.
To provide feedback on the documentation, create new issues at Microsoft/vscode-docs. If you have extension questions that you cannot find an answer for, or issues with the VS Code Extension API, please open new issues at Microsoft/vscode.
---
title: "AI-Powered Extensions"
category: "extension-guides"
tags: ["AI", "machine learning", "intelligence"]
---

AI extensibility in VS Code
This article provides an overview of AI extensibility options in Visual Studio Code, helping you choose the right approach for your extension.

VS Code includes powerful AI features that enhance the coding experience:

Code completion: Offers inline code suggestions as you type
Agent mode: Enables AI to autonomously plan and execute development tasks with specialized tools
Chat: Lets developers use natural language to ask questions or make edits in codebase through chat interfaces
Smart actions: Use AI-enhanced actions for common development tasks, integrated throughout the editor
You can extend and customize each of these built-in capabilities to create tailored AI experiences that meet the specific needs of your users.

Why extend AI in VS Code?
Adding AI capabilities to your extension brings several benefits to your users:

Domain-specific knowledge in agent mode: Let agent mode access your company's data sources and services
Enhanced user experience: Provide intelligent assistance tailored to your extension's domain
Domain specialization: Create AI features specific to a programming language, framework, or domain
Extend chat capabilities: Add specialized tools or assistants to the chat interface for more powerful interactions
Improved developer productivity: Enhance common developer tasks, like debugging, code reviewing or testing, with AI capabilities
Extend the chat experience
Language model tool
Language model tools enable you to extend agent mode in VS Code with domain-specific capabilities. In agent mode, these tools are automatically invoked based on the user's chat prompt to perform specialized tasks or retrieve information from a data source or service. Users can also reference these tools explicitly in their chat prompt by #-mentioning the tool.

To implement a language model tool, use the Language Model Tools API within your VS Code extension. A language model tool can access all VS Code extension APIs and provide deep integration with the editor.

Key benefits:

Domain-specific capabilities as part of an autonomous coding workflow
Your tool implementation can use VS Code APIs since it runs in the extension host process
Easy distribution and deployment via the Visual Studio Marketplace
Key considerations:

Remote deployment requires the extension to implement the client-server communication
Reuse across different tools requires modular design and implementation
MCP tool
Model Context Protocol (MCP) tools provide a way to integrate external services with language models by using a standardized protocol. In agent mode, these tools are automatically invoked based on the user's chat prompt to perform specialized tasks or retrieve information from external data sources.

MCP tools run outside of VS Code, either locally on the user's machine or as a remote service. Users can add MCP tools through JSON configuration or VS Code extension can configure them programmatically. You can implement MCP tools through various language SDKs and deployment options.

As MCP tools run outside of VS Code, they do not have access to the VS Code extension APIs.

Key benefits:

Add domain-specific capabilities as part of an autonomous coding workflow
Local and remote deployment options
Reuse MCP servers in other MCP clients
Key considerations:

No access to VS Code extension APIs
Distribution and deployment require users to set up the MCP server
Chat participant
Chat participants are specialized assistants that enable users to extend ask mode with domain-specific experts. In chat, users can invoke a chat participant by @-mentioning it and passing in a natural language prompt about a particular topic or domain. The chat participant is responsible for handling the entire chat interaction.

To implement a chat participant, use the Chat API within your VS Code extension. A chat participant can access all VS Code extension APIs and provide deep integration with the editor.

Key benefits:

Control the end-to-end interaction flow
Running in the extension host process allows access to VS Code extension APIs
Easy distribution and deployment via the Visual Studio Marketplace
Key considerations:

Remote deployment requires the extension to implement the client-server communication
Reuse across different tools requires modular design and implementation
Build your own AI-powered features
VS Code gives you direct programmatic access to AI models for creating custom AI-powered features in your extensions. This approach enables you to build editor-specific interactions that use AI capabilities without relying on the chat interface.

To use language models directly, use the Language Model API within your VS Code extension. You can incorporate these AI capabilities into any extension feature, such as code actions, hover providers, custom views, and more.

Key benefits:

Integrate AI capabilities into existing extension features or build new ones
Running in the extension host process allows access to VS Code extension APIs
Easy distribution and deployment via the Visual Studio Marketplace
Key considerations:

Reuse across different experiences requires modular design and implementation
Decide which option to use
When choosing the right approach for extending AI in your VS Code extension, consider the following guidelines:

Choose Language Model Tool when:

You want to extend chat in VS Code with specialized capabilities
You want automatic invocation based on user intent in agent mode
You want access to VS Code APIs for deep integration in VS Code
You want to distribute your tool through the VS Code Marketplace
Choose MCP Tool when:

You want to extend chat in VS Code with specialized capabilities
You want automatic invocation based on user intent in agent mode
You don't need to integrate with VS Code APIs
Your tool needs to work across different environments (not just VS Code)
Your tool should run remotely or locally
Choose Chat Participant when:

You want to extend ask mode with a specialized assistant with domain expertise
You need to customize the entire interaction flow and response behavior
You want access to VS Code APIs for deep integration in VS Code
You want to distribute your tool through the VS Code Marketplace
Choose Language Model API when:

You want to integrate AI capabilities into existing extension features
You're building UI experiences outside the chat interface
You need direct programmatic control over AI model requests
Next steps
Choose the approach that best fits your extension's goals:

Implement a language model tool
Register MCP tools in your VS Code extension
Integrate AI in your extension with the Language Model API
Implement a chat participant
Extend code completions with the Inline Completions API
Sample projects
Chat sample: Extension with agent mode tool and chat participant
Code tutor chat participant tutorial: Building a specialized chat assistant
AI-powered code annotations tutorial: Step-by-step guide for using the Language Model API
MCP extension sample: Extension that registers an MCP tool



Language Model Tool API
Language model tools enable you to extend the functionality of a large language model (LLM) in chat with domain-specific capabilities. To process a user's chat prompt, agent mode in VS Code can automatically invoke these tools to perform specialized tasks as part of the conversation. By contributing a language model tool in your VS Code extension, you can extend the agentic coding workflow while also providing deep integration with the editor.

In this extension guide, you learn how to create a language model tool by using the Language Model Tools API and how to implement tool calling in a chat extension.

You can also extend the chat experience with specialized tools by contributing an MCP server. See the AI Extensibility Overview for details on the different options and how to decide which approach to use.

What is tool calling in an LLM?
A language model tool is a function that can be invoked as part of a language model request. For example, you might have a function that retrieves information from a database, performs some calculation, or calls an online API. When you contribute a tool in a VS Code extension, agent mode can then invoke the tool based on the context of the conversation.

The LLM never actually executes the tool itself, instead the LLM generates the parameters that are used to call your tool. It's important to clearly describe the tool's purpose, functionality, and input parameters so that the tool can be invoked in the right context.

The following diagram shows the tool-calling flow in agent mode in VS Code. See Tool-calling flow for details about the specific steps involved.

Diagram that shows the Copilot tool-calling flow

Read more about function calling in the OpenAI documentation.

Why implement a language model tool in your extension?
Implementing a language model tool in your extension has several benefits:

Extend agent mode with specialized, domain-specific, tools that are automatically invoked as part of responding to a user prompt. For example, enable database scaffolding and querying to dynamically provide the LLM with relevant context.
Deeply integrate with VS Code by using the broad set of extension APIs. For example, use the debug APIs to get the current debugging context and use it as part of the tool's functionality.
Distribute and deploy tools via the Visual Studio Marketplace, providing a reliable and seamless experience for users. Users don't need a separate installation and update process for your tool.
You might consider implementing a language model tool with an MCP server in the following scenarios:

You already have an MCP server implementation and also want to use it in VS Code.
You want to reuse the same tool across different development environments and platforms.
Your tool is hosted remotely as a service.
You don't need access to VS Code APIs.
Create a language model tool
Implementing a language model tool consists of two main parts:

Define the tool's configuration in the package.json file of your extension.
Implement the tool in your extension code by using the Language Model API reference
You can get started with a basic example project.

1. Static configuration in package.json
The first step to define a language model tool in your extension is to define it in the package.json file of your extension. This configuration includes the tool name, description, input schema, and other metadata:

Add an entry for your tool in the contributes.languageModelTools section of your extension's package.json file.

Give the tool a unique name:

Expand table
Property	Description
name	The unique name of the tool, used to reference the tool in the extension implementation code. Format the name in the format {verb}_{noun}. See naming guidelines.
displayName	The user-friendly name of the tool, used for displaying in the UI.
If the tool can be used in agent mode or referenced in a chat prompt with #, add the following properties:

Users can enable or disable the tool in the Chat view, similar to how this is done for Model Context Protocol (MCP) tools.

Expand table
Property	Description
canBeReferencedInPrompt	Set to true if the tool can be used in agent mode or referenced in chat.
toolReferenceName	The name for users to reference the tool in a chat prompt via #.
icon	The icon to display for the tool in the UI.
userDescription	User-friendly description of the tool, used for displaying in the UI.
Add a detailed description in modelDescription. This information is used by the LLM to determine in which context your tool should be used.

What exactly does the tool do?
What kind of information does it return?
When should and shouldn't it be used?
Describe important limitations or constraints of the tool.
If the tool takes input parameters, add an inputSchema property that describes the tool's input parameters.

This JSON schema describes an object with the properties that the tool takes as input, and whether they are required. File paths should be absolute paths.

Describe what each parameter does and how it relates to the tool's functionality.

Add a when clause to control when the tool is available.

The languageModelTools contribution point lets you restrict when a tool is available for agent mode or can be referenced in a prompt by using a when clause. For example, a tool that gets the debug call stack information, should only be available when the user is debugging.

JSON

"contributes": {
    "languageModelTools": [
        {
            "name": "chat-tools-sample_tabCount",
            ...
            "when": "debugState == 'running'"
        }
    ]
}
Example tool definition
2. Tool implementation
Implement the language model tool by using the Language Model API. This consists of the following steps:

On activation of the extension, register the tool with vscode.lm.registerTool.

Provide the name of the tool as you specified it in the name property in package.json.

If you want the tool to be private to your extension, skip the tool registration step.

TypeScript

export function registerChatTools(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.lm.registerTool('chat-tools-sample_tabCount', new TabCountTool())
  );
}
Create a class that implements the vscode.LanguageModelTool<> interface.

Add tool confirmation messages in the prepareInvocation method.

A generic confirmation dialog will always be shown for tools from extensions, but the tool can customize the confirmation message. Give enough context to the user to understand what the tool is doing. The message can be a MarkdownString containing a code block.

The following example shows how to provide a confirmation message for the tab count tool.

TypeScript

async prepareInvocation(
    options: vscode.LanguageModelToolInvocationPrepareOptions<ITabCountParameters>,
    _token: vscode.CancellationToken
) {
    const confirmationMessages = {
        title: 'Count the number of open tabs',
        message: new vscode.MarkdownString(
            `Count the number of open tabs?` +
            (options.input.tabGroup !== undefined
                ? ` in tab group ${options.input.tabGroup}`
                : '')
        ),
    };

    return {
        invocationMessage: 'Counting the number of tabs',
        confirmationMessages,
    };
}
If prepareInvocation returned undefined, the generic confirmation message will be shown. Note that the user can also select to "Always Allow" a certain tool.

Define an interface that describes the tool input parameters.

The interface is used in the invoke method of the vscode.LanguageModelTool class. The input parameters are validated against the JSON schema you defined in the inputSchema in package.json.

The following example shows the interface for the tab count tool.

TypeScript

export interface ITabCountParameters {
  tabGroup?: number;
}
Implement the invoke method. This method is called when the language model tool is invoked while processing a chat prompt.

The invoke method receives the tool input parameters in the options parameter. The parameters are validated against the JSON schema defined in inputSchema in package.json.

When an error occurs, throw an error with a message that makes sense to the LLM. Optionally, provide instructions on what the LLM should do next, such as retrying with different parameters, or performing a different action.

The following example shows the implementation of the tab count tool. The result of the tool is an instance of type vscode.LanguageModelToolResult.

TypeScript

async invoke(
    options: vscode.LanguageModelToolInvocationOptions<ITabCountParameters>,
    _token: vscode.CancellationToken
) {
    const params = options.input;
    if (typeof params.tabGroup === 'number') {
        const group = vscode.window.tabGroups.all[Math.max(params.tabGroup - 1, 0)];
        const nth =
            params.tabGroup === 1
                ? '1st'
                : params.tabGroup === 2
                    ? '2nd'
                    : params.tabGroup === 3
                        ? '3rd'
                        : `${params.tabGroup}th`;
        return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(`There are ${group.tabs.length} tabs open in the ${nth} tab group.`)]);
    } else {
        const group = vscode.window.tabGroups.activeTabGroup;
        return new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(`There are ${group.tabs.length} tabs open.`)]);
    }
}
View the full source code for implementing a language model tool in the VS Code Extension Samples repository.

Tool-calling flow
When a user sends a chat prompt, the following steps occur:

Copilot determines the list of available tools based on the user's configuration.

The list of tools consists of built-in tools, tools registered by extensions, and tools from MCP servers. You can contribute to agent mode via extensions or MCP servers (shown in green in the diagram).

Copilot sends the request to the LLM and provides it with the prompt, chat context, and the list of tool definitions to consider.

The LLM generates a response, which might include one or more requests to invoke a tool.

If needed, Copilot invokes the suggested tool(s) with the parameter values provided by the LLM.

A tool response might result in more requests for tool invocations.

If there are errors or follow-up tool requests, Copilot iterates over the tool-calling flow until all tool requests are resolved.

Copilot returns the final response to the user, which might include responses from multiple tools.

Guidelines and conventions
Naming: write clear and descriptive names for tools and parameters.

Tool name: should be unique, and clearly describe their intent. Structure the tool name in the format {verb}_{noun}. For example, get_weather, get_azure_deployment, or get_terminal_output.

Parameter name: should describe the parameter's purpose. Structure the parameter name in the format {noun}. For example, destination_location, ticker, or file_name.

Descriptions: write detailed descriptions for tools and parameters.

Describe what the tool does and when it should and shouldn't be used. For example, "This tool retrieves the weather for a given location."
Describe what each parameter does and how it relates to the tool's functionality. For example, "The destination_location parameter specifies the location for which to retrieve the weather. It should be a valid location name or coordinates."
Describe important limitations or constraints of the tool. For example, "This tool only retrieves weather data for locations in the United States. It might not work for other regions."
User confirmation: provide a confirmation message for the tool invocation. A generic confirmation dialog will always be shown for tools from extensions, but the tool can customize the confirmation message. Give enough context to the user to understand what the tool is doing.

Error handling: when an error occurs, throw an error with a message that makes sense to the LLM. Optionally, provide instructions on what the LLM should do next, such as retrying with different parameters, or performing a different action.

Get more best practices for creating tools in the OpenAI documentation and Anthropic documentation.

Related content
Language Model API reference
Register an MCP server in a VS Code extension
Use MCP tools in agent mode



MCP developer guide
Model Context Protocol (MCP) is an open standard that enables AI models to interact with external tools and services through a unified interface. Visual Studio Code implements the full MCP specification, enabling you to create MCP servers that provide tools, prompts, and resources for extending the capabilities of AI agents in VS Code.

This guide covers everything you need to know to build MCP servers that work seamlessly with VS Code and other MCP clients.

Important
MCP support in VS Code is currently in preview.

Why use MCP servers?
Implementing an MCP server to extend chat in VS Code with language model tools has the following benefits:

Extend agent mode with specialized, domain-specific, tools that are automatically invoked as part of responding to a user prompt. For example, enable database scaffolding and querying to dynamically provide the LLM with relevant context.
Flexible deployment options for local and remote scenarios.
Reuse your MCP server across different tools and platforms.
You might consider implementing a language model tool with the Language Model API in the following scenarios:

You want to deeply integrate with VS Code by using extension APIs.
You want to distribute your tool and updates by using the Visual Studio Marketplace.
Add MCP servers to VS Code
Users can add MCP servers within VS Code in several ways:

Workspace configuration: Specify the server configuration in a .vscode/mcp.json file in the workspace.
Global configuration: Define servers globally in the user profile.
Autodiscovery: VS Code can discover servers from other tools like Claude Desktop.
Extension: VS Code extensions can register MCP servers programmatically.
In addition, users can trigger MCP installation by opening a special URL (vscode:mcp/install), which is used in the MCP gallery on the VS Code website. Users can access the gallery directly from the MCP view in the Extensions view.

Finally, install MCP servers from the command line with the --add-mcp command-line option.

Manage MCP servers
You can manage the list of installed MCP servers from the Extension view (Ctrl+Shift+X) in VS Code.

Screenshot showing the MCP servers in the Extensions view.

Right-click on an MCP server or select the gear icon to perform the following actions:

Start/Stop/Restart: Start, stop, or restart the MCP server.
Disconnect Account: Disconnect the account for authentication with the MCP server.
Show Output: View the server logs to diagnose issues.
Show Configuration: View the MCP server configuration.
Configure Model Access: Configure which models the MCP server can access (sampling).
Show Sampling Requests: View the sampling requests made by the MCP server.
Browse Resources: View the resources provided by the MCP server.
Uninstall: Uninstall the MCP server from your environment.
Alternatively, run the MCP: List Servers command from the Command Palette to view the list of configured MCP servers. You can then select a server and perform actions on it.

Tip
When you open the .vscode/mcp.json file, VS Code shows commands to start, stop, or restart a server directly from the editor.

MCP server configuration with lenses to manage server.

MCP URL handler
VS Code provides a URL handler for installing an MCP server from a link. To form the URL, construct an obj object in the same format as you would provide to --add-mcp, and then create the link by using the following logic:

TypeScript

// For Insiders, use `vscode-insiders` instead of `code`
const link = `vscode:mcp/install?${encodeURIComponent(JSON.stringify(obj))}`;
This link can be used in a browser, or opened on the command line, for example via xdg-open $LINK on Linux.

MCP features supported by VS Code
VS Code supports the following transport methods for MCP servers:

Standard input/output (stdio): Run a server as a local process that communicates over standard input and output
Streamable HTTP (http): Communicate with a (remote) server using HTTP POST and GET
Server-sent events (sse, legacy): Supported with a (remote) server over HTTP using server-sent events
The following MCP features are supported in VS Code:

Tools: Executable actions that can be used in agent mode
Prompts: Reusable chat prompt templates, optionally with parameters, which users can invoke through slash commands(/mcp.servername.promptname) in chat
Resources: Data and content which users can add as chat context or interact with directly in VS Code
Authorization: Authorize access to an MCP server using OAuth
Sampling (Preview): Make language model requests using the user's configured models and subscription
Elicitation: Request input from the user
Workspace roots: Information about the user's workspace structure
For complete specification details, see the Model Context Protocol documentation.

Tools
Tool definition
VS Code supports MCP tools in agent mode, where they are invoked as needed based on the task. Users can enable and configure them with the tools picker. The tool description is shown in the tools picker, alongside the tool name, and in the dialog when asking for confirmation before running a tool.

Screenshot that shows the tools picker in agent mode, highlighting tools from an MCP server.

Users can edit model-generated input parameters in the tool confirmation dialog. The confirmation dialog will be shown for all tools that are not marked with the readOnlyHint annotation.

Screenshot that shows the tool confirmation dialog with input parameters for an MCP tool.

Dynamic tool discovery
VS Code also supports dynamic tool discovery, allowing servers to register tools at runtime. For example, a server can provide different tools based on the framework or language detected in the workspace, or in response to the user's chat prompt.

Tool annotations
To provide extra metadata about a tool's behavior, you can use tool annotations:

title: Human-readable title for the tool, shown in the Chat view when a tool is invoked
readOnlyHint: Optional hint to indicate that the tool is read-only. VS Code doesn't ask for confirmation to run read-only tools.
Resources
Resources enable you to provide data and content to users in a structured way. Users can directly access resources in VS Code, or use them as context in chat prompts. For example, an MCP server could generate screenshots and make them available as resources, or provide access to log files, which are then updated in real-time.

When you define an MCP resource, the resource name is shown in the MCP Resources Quick Picks. Resources can be opened via the MCP: Browse Resources command or attached to a chat request with Add Context and then selecting MCP Resource. Resources can contain text or binary content.

Screenshot that shows the MCP Resources Quick Pick.

VS Code supports resource updates, enabling users to see changes to the contents of a resource in real-time in the editor.

Resource templates
VS Code also supports resource templates, enabling users to provide input parameters when referencing a resource. For example, a database query tool could ask for the database table name.

When accessing a resource with a template, users are prompted for the required parameters in a Quick Pick. You can provide completions to suggest values for the parameter.

Prompts
Prompts are reusable chat prompt templates that users can invoke in chat by using a slash command (mcp.servername.promptname). Prompts can be useful for onboarding users to your servers by highlighting various tools or providing built-in complex workflows that adapt to the user's local context and service.

If you define completions to suggest values for prompt input arguments, then VS Code shows a dialog to collect input from the user.

TypeScript

server.prompt(
  'teamGreeting',
  'Generate a greeting for team members',
  {
    name: completable(z.string(), value => {
      return ['Alice', 'Bob', 'Charlie'].filter(n => n.startsWith(value));
    })
  },
  async ({ name }) => ({
    messages: [
      {
        role: 'assistant',
        content: { type: 'text', text: `Hello ${name}, welcome to the team!` }
      }
    ]
  })
);
Screenshot that shows the prompt dialog for an MCP prompt with input parameters.

Note
Users can enter a terminal command in the prompt dialog and use the command output as input for the prompt.

When you include a resource type in the prompt response, VS Code attaches that resource as context to the chat prompt.

Authorization
VS Code supports MCP servers that require authentication, allowing users to interact with an MCP server that operates on behalf of their user account for that service.

The authorization specification cleanly separates MCP servers as Resource Servers from Authorization Servers, allowing developers to delegate authentication to existing identity providers (IdPs) rather than building their own OAuth implementations from scratch.

VS Code has built-in authentication support for GitHub and Microsoft Entra. If your MCP server implements the latest specification and uses GitHub or Microsoft Entra as the authorization server, users can manage which MCP servers have access to their account through the Accounts menu > Manage Trusted MCP Servers action for that account.

Screenshot that shows the Accounts menu with the Manage Trusted MCP Servers action.

VS Code supports authorization using OAuth 2.1 standards and 2.0 standards to other IdPs than GitHub and Microsoft Entra. VS Code first starts with a Dynamic Client Registration (DCR) handshake and then falls back to a client-credentials workflow if the IdP does not support DCR. This gives more flexibility to the various IdPs to create static client IDs or specific client ID-secret pairs for each MCP server accordingly.

Users can then view their authentication status also through the Accounts menu. To remove dynamic client registrations, users can use the Authentication: Remove Dynamic Authentication Providers command in the Command Palette.

Below is a checklist to ensure your MCP server and VS Code's OAuth workflows will work:

The MCP server defines the MCP authorization specification.
The IdP must support either DCR or client credentials
The redirect URL list must include these URLs: http://127.0.0.1:33418 and https://vscode.dev/redirect
When DCR is not supported by the MCP server, users will go through the fallback client-credential flow:

Screenshot that shows the authorization when DCR is not supported for a MCP server.

Screenshot that shows the authorization when Client ID for a MCP server is requested.

Screenshot that shows the authorization when Client Secret for a MCP server is requested.

Note
VS Code still supports MCP servers that behave as an authorization server, but it is recommended to use the latest specification for new servers.

Sampling (Preview)
VS Code provides access to sampling for MCP servers. This allows your MCP server to make language model requests using the user's configured models and subscriptions. Sampling can be used to summarize large data or extract information before sending it to the client, or to implement smarter agentic decision in tool logic.

The first time an MCP server performs a sampling request, the user is prompted to authorize the server to access their models.

Screenshot that shows the authorization prompt for an MCP server to access models.

Users can specify which models they allow the MCP server to use for sampling by using the MCP: List Servers > Configure Model Access command in the Command Palette. You can specify modelPreferences in your MCP server to provide hints about which models to use for sampling, and VS Code will pick from the allowed models when evaluating the server's preferences

Screenshot that shows the Configure Model Access dialog for an MCP server.

Users can view the sampling requests made by an MCP server with the MCP: List Servers > Show Sampling Requests command in the Command Palette.

Workspace roots
VS Code provides the MCP server with the user's workspace root folder information.

Register an MCP server in your extension
To register an MCP server in your extension, you need to perform the following steps:

Define the MCP server definition provider in the package.json file of your extension.
Implement the MCP server definition provider in your extension code by using the vscode.lm.registerMcpServerDefinitionProvider API.
You can get started with a basic example of how to register an MCP server in a VS Code extension.

1. Static configuration in package.json
Extensions that want to register MCP servers must contribute the contributes.mcpServerDefinitionProviders extension point in the package.json with the id of the provider. This id should match the one used in the implementation.

JSON

{
    ...
    "contributes": {
        "mcpServerDefinitionProviders": [
            {
                "id": "exampleProvider",
                "label": "Example MCP Server Provider"
            }
        ]
    }
    ...
}
2. Implement the provider
To register an MCP server in your extension, use the vscode.lm.registerMcpServerDefinitionProvider API to provide the MCP configuration for the server. The API takes a providerId string and a McpServerDefinitionProvider object.

The McpServerDefinitionProvider object has three properties:

onDidChangeMcpServerDefinitions: event that is triggered when the MCP server configurations change.
provideMcpServerDefinitions: function that returns an array of MCP server configurations (vscode.McpServerDefinition[]).
resolveMcpServerDefinition: function that the editor calls when the MCP server needs to be started. Use this function to perform additional actions that may require user interaction, such as authentication.
An McpServerDefinition object can be one of the following types:

vscode.McpStdioServerDefinition: represents an MCP server available by running a local process and operating on its stdin and stdout streams.
vscode.McpHttpServerDefinition: represents an MCP server available using the Streamable HTTP transport.
Example MCP server definition provider
Troubleshoot and debug MCP servers
MCP development mode in VS Code
When developing MCP servers, you can enable MCP development mode in VS Code. To enable development mode, add the dev property to your MCP server configuration and specify the following properties:

watch: A glob pattern to watch for file changes to files and automatically restart the server
debug: Debugger to attach to your MCP server process when starting it (currently only supported for servers launched with node or python)
The following example shows how to configure a Node.js MCP server that watches for changes to TypeScript files in the src directory and uses the Node.js debugger:

JSON

{
  "servers": {
    "my-mcp-server": {
      "type": "stdio",
      "command": "node",
      "cwd": "${workspaceFolder}",
      "args": ["./build/index.js"],
      "dev": {
        "watch": "src/**/*.ts",
        "debug": { "type": "node" }
      }
    }
  }
}
MCP output log
When VS Code encounters an issue with an MCP server, it shows an error indicator in the Chat view.

MCP Server Error

Select the error notification in the Chat view, and then select the Show Output option to view the server logs. Alternatively, run MCP: List Servers from the Command Palette, select the server, and then choose Show Output.

MCP Server Error Output

Best practices
Naming conventions to ensure unique and descriptive names
Implement proper error handling and validation with descriptive error messages
Use progress reporting to inform users about long-running operations
Keep tool operations focused and atomic to avoid complex interactions
Document your tools clearly with descriptions that help users understand when to use them
Handle missing input parameters gracefully by providing default values or clear error messages
Set MIME types for resources to ensure proper handling of different content types in VS Code
Use resource templates to allow users to provide input parameters when accessing resources
Cache resource content to improve performance and reduce unnecessary network requests
Set reasonable token limits for sampling requests to avoid excessive resource usage
Validate sampling responses before using them
Naming conventions
The following naming conventions are recommended for MCP servers and their components:

Expand table
Component	Naming Convention Guidelines
Tool name	
Unique within the MCP server
Describes the action and the target of the action
Use snake case, structured as {verb}_{noun}
Examples: generate_report, fetch_data, analyze_code
Tool input parameter	
Describes the purpose of the parameter
Use camelCase for multi-word parameters
Examples: path, queryString, userId
Resource name	
Unique within the MCP server
Describes the content of the resource
Use title case
Examples: Application Logs, Database Table, GitHub Repository
Resource template parameter	
Describes the purpose of the parameter
Use camelCase for multi-word parameters
Examples: name, repo, fileType
Prompt name	
Unique within the MCP server
Describes the intended use of the prompt
Use camelCase for multi-word parameters
Examples: generateApiRoute, performSecurityReview, analyzeCodeQuality
Prompt input parameter	
Describes the purpose of the parameter
Use camelCase for multi-word parameters
Examples: filePath, queryString, userId
Get started to create an MCP server
VS Code has all the tools you need to develop your own MCP server. While MCP servers can be written in any language that can handle stdout, the MCP's official SDKs are a good place to start:

TypeScript SDK
Python SDK
Java SDK
Kotlin SDK
C# SDK
You might also find the MCP for Beginners curriculum helpful to get started with building your first MCP server.

Related content
Contribute a language model tool
Use MCP tools in agent mode
VS Code curated list of MCP servers
Model Context Protocol Documentation


Chat Participant API
Chat participants are specialized assistants that enable users to extend chat in VS Code with domain-specific experts. Users invoke a chat participant by @-mentioning it, and the participant is then responsible for handling the user's natural language prompt.

In this extension guide, you learn how to create a chat participant by using the Chat Participant API.

VS Code has several built-in chat participants like @vscode, @terminal, or @workspace. They are optimized to answer questions about their respective domains.

Chat participants are different from language model tools that are invoked as part of the LLM orchestrating the steps needed to resolve the user's chat prompt. Chat participants receive the user's prompt and orchestrate the tasks that are needed themselves.

Why implement a chat participant in your extension?
Implementing a chat participant in your extension has several benefits:

Extend chat with specialized, domain-specific knowledge and expertise. For example, the built-in @vscode participant has knowledge about VS Code and its extension APIs.
Own conversation by managing the end-to-end user chat prompt and response.
Deeply integrate with VS Code by using the broad set of extension APIs. For example, use the debug APIs to get the current debugging context and use it as part of the tool's functionality.
Distribute and deploy chat participants via the Visual Studio Marketplace, providing a reliable and seamless experience for users. Users don't need a separate installation and update process.
You might consider implementing a language model tool or MCP server if you want to provide domain-specific capabilities that can be invoked automatically as part of an autonomous, agentic coding session. See the AI Extensibility Overview for details on the different options and how to decide which approach to use.

Parts of the chat user experience
The following screenshot shows the different chat concepts in the Visual Studio Code chat experience for the sample extension.

Chat concepts explanation

Use the @ syntax to invoke the @cat chat participant
Use the / syntax to call the /teach command
User-provided query, also known as the user prompt
Icon and participant fullName that indicate that Copilot is using the @cat chat participant
Markdown response, provided by @cat
Code fragment included in the markdown response
Button included in the @cat response, the button invokes a VS Code command
Suggested follow-up questions provided by the chat participant
Chat input field with the placeholder text provided by the chat participant's description property
Create a chat participant
Implementing a chat participant consists of the following parts:

Define the chat participant in the package.json file of your extension.
Implement a request handler to process the user's chat prompt and return a response.
(Optional) Implement chat slash commands to provide users with a shorthand notation for common tasks.
(Optional) Define suggested follow-up questions.
(Optional) Implement participant detection where VS Code automatically routes a chat request to the appropriate chat participant without explicit mention from the user.
You can get started with a basic example project.

Diagram showing how extension can contribute to chat

1. Register the chat participant
The first step to create a chat extension is to register it in your package.json, with the following properties:

id: A unique identifier for the chat participant, as defined in the package.json file.
name: A short name for the chat participant, used for @-mentions in the chat.
fullName: The full name of the chat participant, displayed in the title area of the response.
description: A brief description of the chat participant's purpose, used as placeholder text in the chat input field.
isSticky: A boolean value indicating whether the chat participant is persistent in the chat input field after responding.
JSON

"contributes": {
        "chatParticipants": [
            {
                "id": "chat-sample.my-participant",
                "name": "my-participant",
                "fullName": "My Participant",
                "description": "What can I teach you?",
                "isSticky": true
            }
        ]
}
We suggest using a lowercase name and using title case for the fullName to align with existing chat participants. Get more info about the naming conventions for chat participants.

Note
Some participant names are reserved. If you use such a reserved name, VS Code displays the fully qualified name of your chat participant (including the extension ID).

2. Implement a request handler
Implement the chat participant by using the Chat Participant API. This consists of the following steps:

On activation of the extension, create the participant with vscode.chat.createChatParticipant.

Provide the ID, which you defined in package.json, and a reference to the request handler that you implement in the next step.

TypeScript

export function activate(context: vscode.ExtensionContext) {
  // Register the chat participant and its request handler
  const cat = vscode.chat.createChatParticipant('chat-sample.my-participant', handler);

  // Optionally, set some properties for @cat
  cat.iconPath = vscode.Uri.joinPath(context.extensionUri, 'cat.jpeg');

  // Add the chat request handler here
}
In the activate function, define the vscode.ChatRequestHandler request handler.

The request handler is responsible for processing the user's chat requests in the VS Code Chat view. Each time a user enters a prompt in the chat input field, the chat request handler is invoked.

TypeScript

const handler: vscode.ChatRequestHandler = async (
  request: vscode.ChatRequest,
  context: vscode.ChatContext,
  stream: vscode.ChatResponseStream,
  token: vscode.CancellationToken
): Promise<ICatChatResult> => {
  // Chat request handler implementation goes here
};
Determine the user's intent from vscode.ChatRequest.

To determine the intent of the user's request, you can reference the vscode.ChatRequest parameter to access the user's prompt text, commands, and chat location.

Optionally, you can take advantage of the language model to determine the user's intent, rather than using traditional logic. As part of the request object you get a language model instance that the user picked in the chat model dropdown. Learn how you can use the Language Model API in your extension.

The following code snippet shows the basic structure of first using the command, and then the user prompt to determine the user intent:

TypeScript

const handler: vscode.ChatRequestHandler = async (
  request: vscode.ChatRequest,
  context: vscode.ChatContext,
  stream: vscode.ChatResponseStream,
  token: vscode.CancellationToken
): Promise<ICatChatResult> => {
  // Test for the `teach` command
  if (request.command == 'teach') {
    // Add logic here to handle the teaching scenario
    doTeaching(request.prompt, request.variables);
  } else {
    // Determine the user's intent
    const intent = determineUserIntent(request.prompt, request.variables, request.model);

    // Add logic here to handle other scenarios
  }
};
Add logic to process the user request.

Often, chat extensions use the request.model language model instance to process the request. In this case, you might adjust the language model prompt to match the user's intent.

Alternately, you can implement the extension logic by invoking a backend service, by using traditional programming logic, or by using a combination of all these options. For example, you could invoke a web search to gather additional information, which you then provide as context to the language model.

While processing the current request, you might want to refer to previous chat messages. For example, if a previous response returned a C# code snippet, the user's current request might be "give the code in Python". Learn how you can use the chat message history.

If you want to process a request differently based on the location of the chat input (Chat view, Quick Chat, inline chat), you can use the location property of the vscode.ChatRequest. For example, if the user sends a request from the terminal inline chat, you might look up a shell command. Whereas, if the user uses the Chat view, you could return a more elaborate response.

Return the chat response to the user.

Once you've processed the request, you have to return a response to the user in the Chat view. You can use streaming to respond to user queries.

Responses can contain different content types: Markdown, images, references, progress, buttons, and file trees.

Response from the cat extension that includes code, markdown and a button

An extension can use the response stream in the following way:

TypeScript

stream.progress('Picking the right topic to teach...');
stream.markdown(`\`\`\`typescript
const myStack = new Stack();
myStack.push(1); // pushing a number on the stack (or let's say, adding a fish to the stack)
myStack.push(2); // adding another fish (number 2)
console.log(myStack.pop()); // eating the top fish, will output: 2
\`\`\`
So remember, Code Kitten, in a stack, the last fish in is the first fish out - which we tech cats call LIFO (Last In, First Out).`);

stream.button({
  command: 'cat.meow',
  title: vscode.l10n.t('Meow!'),
  arguments: []
});
Get more info about the supported chat response output types.

In practice, extensions typically send a request to the language model. Once they get a response from the language model, they might further process it, and decide if they should stream anything back to the user. The VS Code Chat API is streaming-based, and is compatible with the streaming Language Model API. This allows extensions to report progress and results continuously with the goal of having a smooth user experience. Learn how you can use the Language Model API.

3. Register slash commands
A chat participant can contribute slash commands, which are shortcuts to specific functionality provided by the extension. Users can reference slash commands in chat by using the / syntax, for example /explain.

One of the tasks when answering questions is to determine the user intent. For example, VS Code could infer that Create a new workspace with Node.js Express Pug TypeScript means that you want a new project, but @workspace /new Node.js Express Pug TypeScript is more explicit, concise, and saves typing time. If you type / in the chat input field, VS Code offers a list of registered commands with their description.

List of commands in chat for @workspace

Chat participants can contribute slash commands with their description by adding them in package.json:

TypeScript

"contributes": {
    "chatParticipants": [
        {
            "id": "chat-sample.cat",
            "name": "cat",
            "fullName": "Cat",
            "description": "Meow! What can I teach you?",
            "isSticky": true,
            "commands": [
                {
                    "name": "teach",
                    "description": "Pick at random a computer science concept then explain it in purfect way of a cat"
                },
                {
                    "name": "play",
                    "description": "Do whatever you want, you are a cat after all"
                }
            ]
        }
    ]
}
Get more info about the naming conventions for slash commands.

4. Register follow-up requests
After each chat request, VS Code invokes follow-up providers to get suggested follow-up questions to show to the user. The user can then select the follow-up question, and immediately send it to the chat extension. Follow-up questions can provide inspiration to the user to take the conversation further, or to discover more capabilities of the chat extension.

The following code snippet shows how to register follow-up requests in a chat extension:

TypeScript

cat.followupProvider = {
    provideFollowups(result: ICatChatResult, context: vscode.ChatContext, token: vscode.CancellationToken) {
        if (result.metadata.command === 'teach') {
            return [{
                prompt: 'let us play',
                title: vscode.l10n.t('Play with the cat')
            } satisfies vscode.ChatFollowup];
        }
    }
};
Tip
Follow-ups should be written as questions or directions, not just concise commands.

5. Implement participant detection
To make it easier to use chat participants with natural language, you can implement participant detection. Participant detection is a way to automatically route the user's question to a suitable participant, without having to explicitly mention the participant in the prompt. For example, if the user asks "How do I add a login page to my project?", the question would be automatically routed to the @workspace participant because it can answer questions about the user's project.

VS Code uses the chat participant description and examples to determine which participant to route a chat prompt to. You can specify this information in the disambiguation property in the extension package.json file. The disambiguation property contains a list of detection categories, each with a description and examples.

Expand table
Property	Description	Examples
category	The detection category. If the participant serves different purposes, you can have a category for each.	
cat
workspace_questions
web_questions
description	A detailed description of the kinds of questions that are suitable for this participant.	
The user wants to learn a specific computer science topic in an informal way.
The user just wants to relax and see the cat play.
examples	A list of representative example questions.	
Teach me C++ pointers using metaphors
Explain to me what is a linked list in a simple way
Can you show me a cat playing with a laser pointer?
You can define participant detection for the overall chat participant, for specific commands, or a combination of both.

The following code snippet shows how to implement participant detection at the participant level.

JSON

"contributes": {
    "chatParticipants": [
        {
            "id": "chat-sample.cat",
            "fullName": "Cat",
            "name": "cat",
            "description": "Meow! What can I teach you?",

            "disambiguation": [
                {
                    "category": "cat",
                    "description": "The user wants to learn a specific computer science topic in an informal way.",
                    "examples": [
                        "Teach me C++ pointers using metaphors",
                        "Explain to me what is a linked list in a simple way",
                        "Can you explain to me what is a function in programming?"
                    ]
                }
            ]
        }
    ]
}
Similarly, you can also configure participant detection at the command level by adding a disambiguation property for one or more items in the commands property.

Apply the following guidelines to improve the accuracy of participant detection for your extension:

Be specific: The description and examples should be as specific as possible to avoid conflicts with other participants. Avoid using generic terminology in the participant and command information.
Use examples: The examples should be representative of the kinds of questions that are suitable for the participant. Use synonyms and variations to cover a wide range of user queries.
Use natural language: The description and examples should be written in natural language, as if you were explaining the participant to a user.
Test the detection: Test the participant detection with a variation of example questions and verify there's no conflict with built-in chat participants.
Note
Built-in chat participants take precedence for participant detection. For example, a chat participant that operates on workspace files might conflict with the built-in @workspace participant.

Use the chat message history
Participants have access to the message history of the current chat session. A participant can only access messages where it was mentioned. A history item is either a ChatRequestTurn or a ChatResponseTurn. For example, use the following code snippet to retrieve all the previous requests that the user sent to your participant in the current chat session:

TypeScript

const previousMessages = context.history.filter(h => h instanceof vscode.ChatRequestTurn);
History will not be automatically included in the prompt, it is up to the participant to decide if it wants to add history as additional context when passing messages to the language model.

Supported chat response output types
To return a response to a chat request, you use the ChatResponseStream parameter on the ChatRequestHandler.

The following list provides the output types for a chat response in the Chat view. A chat response can combine multiple different output types.

Markdown

Render a fragment of Markdown text simple text or images. You can use any Markdown syntax that is part of the CommonMark specification. Use the ChatResponseStream.markdown method and provide the Markdown text.

Example code snippet:

TypeScript

// Render Markdown text
stream.markdown('# This is a title \n');
stream.markdown('This is stylized text that uses _italics_ and **bold**. ');
stream.markdown('This is a [link](https://code.visualstudio.com).\n\n');
stream.markdown('![VS Code](https://code.visualstudio.com/assets/favicon.ico)');
Code block

Render a code block that supports IntelliSense, code formatting, and interactive controls to apply the code to the active editor. To show a code block, use the ChatResponseStream.markdown method and apply the Markdown syntax for code blocks (using backticks).

Example code snippet:

TypeScript

// Render a code block that enables users to interact with
stream.markdown('```bash\n');
stream.markdown('```ls -l\n');
stream.markdown('```');
Command link

Render a link inline in the chat response that users can select to invoke a VS Code command. To show a command link, use the ChatResponseStream.markdown method and use the Markdown syntax for links [link text](command:commandId), where you provide the command ID in the URL. For example, the following link opens the Command Palette: [Command Palette](command:workbench.action.showCommands).

To protect against command injection when you load the Markdown text from a service, you have to use a vscode.MarkdownString object with the isTrusted property set to the list of trusted VS Code command IDs. This property is required to enable the command link to work. If the isTrusted property is not set or a command is not listed, the command link will not work.

Example code snippet:

TypeScript

// Use command URIs to link to commands from Markdown
let markdownCommandString: vscode.MarkdownString = new vscode.MarkdownString(
  `[Use cat names](command:${CAT_NAMES_COMMAND_ID})`
);
markdownCommandString.isTrusted = { enabledCommands: [CAT_NAMES_COMMAND_ID] };

stream.markdown(markdownCommandString);
If the command takes arguments, you need to first JSON encode the arguments and then encode the JSON string as a URI component. You then append the encoded arguments as a query string to the command link.

TypeScript

// Encode the command arguments
const encodedArgs = encodeURIComponent(JSON.stringify(args));

// Use command URIs with arguments to link to commands from Markdown
let markdownCommandString: vscode.MarkdownString = new vscode.MarkdownString(
  `[Use cat names](command:${CAT_NAMES_COMMAND_ID}?${encodedArgs})`
);
markdownCommandString.isTrusted = { enabledCommands: [CAT_NAMES_COMMAND_ID] };

stream.markdown(markdownCommandString);
Command button

Render a button that invokes a VS Code command. The command can be a built-in command or one that you define in your extension. Use the ChatResponseStream.button method and provide the button text and command ID.

Example code snippet:

TypeScript

// Render a button to trigger a VS Code command
stream.button({
  command: 'my.command',
  title: vscode.l10n.t('Run my command')
});
File tree

Render a file tree control that lets users preview individual files. For example, to show a workspace preview when proposing to create a new workspace. Use the ChatResponseStream.filetree method and provide an array of file tree elements and the base location (folder) of the files.

Example code snippet:

TypeScript

// Create a file tree instance
var tree: vscode.ChatResponseFileTree[] = [
  {
    name: 'myworkspace',
    children: [{ name: 'README' }, { name: 'app.js' }, { name: 'package.json' }]
  }
];

// Render the file tree control at a base location
stream.filetree(tree, baseLocation);
Progress message

Render a progress message during a long-running operation to provide the user with intermediate feedback. For example, to report the completion of each step in a multi-step operation. Use the ChatResponseStream.progress method and provide the message.

Example code snippet:

TypeScript

// Render a progress message
stream.progress('Connecting to the database.');
Reference

Add a reference for an external URL or editor location in the list references to indicate which information you use as context. Use the ChatResponseStream.reference method and provide the reference location.

Example code snippet:

TypeScript

const fileUri: vscode.Uri = vscode.Uri.file('/path/to/workspace/app.js'); // On Windows, the path should be in the format of 'c:\\path\\to\\workspace\\app.js'
const fileRange: vscode.Range = new vscode.Range(0, 0, 3, 0);
const externalUri: vscode.Uri = vscode.Uri.parse('https://code.visualstudio.com');

// Add a reference to an entire file
stream.reference(fileUri);

// Add a reference to a specific selection within a file
stream.reference(new vscode.Location(fileUri, fileRange));

// Add a reference to an external URL
stream.reference(externalUri);
Inline reference

Add an inline reference to a URI or editor location. Use the ChatResponseStream.anchor method and provide the anchor location and optional title. To reference a symbol (for example, a class or variable), you would use a location in an editor.

Example code snippet:

TypeScript

const symbolLocation: vscode.Uri = vscode.Uri.parse('location-to-a-symbol');

// Render an inline anchor to a symbol in the workspace
stream.anchor(symbolLocation, 'MySymbol');
Important: Images and links are only available when they originate from a domain that is in the trusted domain list. Get more info about link protection in VS Code.

Implement tool calling
To respond to a user request, a chat extension can invoke language model tools. Learn more about language model tools and the tool-calling flow.

You can implement tool calling in two ways:

By using the @vscode/chat-extension-utils library to simplify the process of calling tools in a chat extension.
By implementing tool calling yourself, which gives you more control over the tool-calling process. For example, to perform additional validation or to handle tool responses in a specific way before sending them to the LLM.
Implement tool calling with the chat extension library
You can use the @vscode/chat-extension-utils library to simplify the process of calling tools in a chat extension.

Implement tool calling in the vscode.ChatRequestHandler function of your chat participant.

Determine the relevant tools for the current chat context. You can access all available tools by using vscode.lm.tools.

The following code snippet shows how to filter the tools to only those that have a specific tag.

TypeScript

const tools =
  request.command === 'all'
    ? vscode.lm.tools
    : vscode.lm.tools.filter(tool => tool.tags.includes('chat-tools-sample'));
Send the request and tool definitions to the LLM by using sendChatParticipantRequest.

TypeScript

const libResult = chatUtils.sendChatParticipantRequest(
  request,
  chatContext,
  {
    prompt: 'You are a cat! Answer as a cat.',
    responseStreamOptions: {
      stream,
      references: true,
      responseText: true
    },
    tools
  },
  token
);
The ChatHandlerOptions object has the following properties:

prompt: (optional) Instructions for the chat participant prompt.
model: (optional) The model to use for the request. If not specified, the model from the chat context is used.
tools: (optional) The list of tools to consider for the request.
requestJustification: (optional) A string that describes why the request is being made.
responseStreamOptions: (optional) Enable sendChatParticipantRequest to stream the response back to VS Code. Optionally, you can also enable references and/or response text.
Return the result from the LLM. This might contain error details or tool-calling metadata.

TypeScript

return await libResult.result;
The full source code of this tool-calling sample is available in the VS Code Extension Samples repository.

Implement tool calling yourself
For more advanced scenarios, you can also implement tool calling yourself. Optionally, you can use the @vscode/prompt-tsx library for crafting the LLM prompts. By implementing tool calling yourself, you have more control over the tool-calling process. For example, to perform additional validation or to handle tool responses in a specific way before sending them to the LLM.

View the full source code for implementing tool calling by using prompt-tsx in the VS Code Extension Samples repository.

Measuring success
We recommend that you measure the success of your participant by adding telemetry logging for Unhelpful user feedback events, and for the total number of requests that your participant handled. An initial participant success metric can then be defined as: unhelpful_feedback_count / total_requests.

TypeScript

const logger = vscode.env.createTelemetryLogger({
  // telemetry logging implementation goes here
});

cat.onDidReceiveFeedback((feedback: vscode.ChatResultFeedback) => {
  // Log chat result feedback to be able to compute the success metric of the participant
  logger.logUsage('chatResultFeedback', {
    kind: feedback.kind
  });
});
Any other user interaction with your chat response should be measured as a positive metric (for example, the user selecting a button that was generated in a chat response). Measuring success with telemetry is crucial when working with AI, since it is a nondeterministic technology. Run experiments, measure and iteratively improve your participant to ensure a good user experience.

Guidelines and conventions
Guidelines
Chat participants should not be purely question-answering bots. When building a chat participant, be creative and use the existing VS Code API to create rich integrations in VS Code. Users also love rich and convenient interactions, such as buttons in your responses, menu items that bring users to your participant in chat. Think about real life scenarios where AI can help your users.

It doesn't make sense for every extension to contribute a chat participant. Having too many participants in chat might lead to a bad user experience. Chat participants are best when you want to control the full prompt, including instructions to the language model. You can reuse the carefully crafted Copilot system message and you can contribute context to other participants.

For example, language extensions (such as the C++ extension) can contribute in various other ways:

Contribute tools that bring language service smarts to the user query. For example, the C++ extension could resolve the #cpp tool to the C++ state of the workspace. This gives the Copilot language model the right C++ context to improve the quality of Copilot answers for C++.
Contribute smart actions that use the language model, optionally in combination with traditional language service knowledge, to deliver a great user experience. For example, C++ might already offer an "extract to method" smart action that uses the language model to generate a fitting default name for the new method.
Chat extensions should explicitly ask for user consent if they are about to do a costly operation or are about to edit or delete something that can't be undone. To have a great user experience, we discourage extensions from contributing multiple chat participants. Up to one chat participant per extension is a simple model that scales well in the UI.

Chat participant naming conventions
Expand table
Property	Description	Naming guidelines
id	Globally unique identifier for the chat participant	
String value
Use the extension name as a prefix, followed by a unique ID for your extension
Example: chat-sample.cat, code-visualizer.code-visualizer-participant
name	Name of the chat participant, referenced by users through the @ symbol	
String value consisting of alphanumeric characters, underscores, and hyphens
It's recommended to only use lowercase to ensure consistency with existing chat participants
Ensure the purpose of the participant is obvious from its name by referencing your company name or its functionality
Some participant names are reserved. If you use a reserved name, the fully qualified name is shown, including the extension ID
Examples: vscode, terminal, code-visualizer
fullName	(Optional) The full name of the participant, which is shown as the label for responses coming from the participant	
String value
It's recommended to use title case
Use your company name, brand name, or user-friendly name for your participant
Examples: GitHub Copilot, VS Code, Math Tutor
description	(Optional) Short description of what the chat participant does, shown as placeholder text in the chat input field or in the list of participants	
String value
It's recommended to use sentence case, without punctuation at the end
Keep the description short to avoid horizontal scrolling
Examples: Ask questions about VS Code, Generate UML diagrams for your code
When referring to your chat participant in any of the user-facing elements, such as properties, chat responses, or chat user interface, it's recommended to not use the term participant, as it's the name of the API. For example, the @cat extension could be called "Cat extension for GitHub Copilot".

Slash command naming conventions
Expand table
Property	Description	Naming guidelines
name	Name of the slash command, referenced by users through the / symbol	
String value
It's recommended to use lower camel case to align with existing slash commands
Ensure the purpose of the command is obvious from its name
Examples: fix, explain, runCommand
description	(Optional) Short description of what the slash command does, shown as placeholder text in the chat input field or in the list of participants and commands	
String value
It's recommended to use sentence case, without punctuation at the end
Keep the description short to avoid horizontal scrolling
Examples: Search for and execute a command in VS Code, Generate unit tests for the selected code
Publishing your extension
Once you have created your AI extension, you can publish your extension to the Visual Studio Marketplace:

Before publishing to the VS Marketplace we recommend that you read the Microsoft AI tools and practices guidelines. These guidelines provide best practices for the responsible development and use of AI technologies.
By publishing to the VS Marketplace, your extension is adhering to the GitHub Copilot extensibility acceptable development and use policy.
Upload to the Marketplace as described in Publishing Extension.
If your extension already contributes functionality other than chat, we recommend that you do not introduce an extension dependency on GitHub Copilot in the extension manifest. This ensures that extension users that do not use GitHub Copilot can use the non-chat functionality without having to install GitHub Copilot.
Extending GitHub Copilot via GitHub Apps
Alternatively, it is possible to extend GitHub Copilot by creating a GitHub App that contributes a chat participant in the Chat view. A GitHub App is backed by a service and works across all GitHub Copilot surfaces, such as github.com, Visual Studio, or VS Code. On the other hand, GitHub Apps do not have full access to the VS Code API. To learn more about extending GitHub Copilot through a GitHub App see the GitHub documentation.

Using the language model
Chat participants can use the language model in a wide range of ways. Some participants only make use of the language model to get answers to custom prompts, for example the sample chat participant. Other participants are more advanced and act like autonomous agents that invoke multiple tools with the help of the language model. An example of such an advanced participant is the built-in @workspace that knows about your workspace and can answer questions about it. Internally, @workspace is powered by multiple tools: GitHub's knowledge graph, combined with semantic search, local code indexes, and VS Code's language services.

Related content
Chat Participant API Reference
Use the Language Model API in your extension
Contribute a language model tool



Language Model API
The Language Model API enables you to use the Language Model and integrate AI-powered features and natural language processing in your Visual Studio Code extension.

You can use the Language Model API in different types of extensions. A typical use for this API is in chat extensions, where you use a language model to interpret the user's request and help provide an answer. However, the use of the Language Model API is not limited to this scenario. You might use a language model in a language or debugger extension, or as part of a command or task in a custom extension. For example, the Rust extension might use the Language Model to offer default names to improve its rename experience.

The process for using the Language Model API consists of the following steps:

Build the language model prompt
Send the language model request
Interpret the response
The following sections provide more details on how to implement these steps in your extension.

To get started, you can explore the chat extension sample.

Build the language model prompt
To interact with a language model, extensions should first craft their prompt, and then send a request to the language model. You can use prompts to provide instructions to the language model on the broad task that you're using the model for. Prompts can also define the context in which user messages are interpreted.

The Language Model API supports two types of messages when building the language model prompt:

User - used for providing instructions and the user's request
Assistant - used for adding the history of previous language model responses as context to the prompt
Note: Currently, the Language Model API doesn't support the use of system messages.

You can use two approaches for building the language model prompt:

LanguageModelChatMessage - create the prompt by providing one or more messages as strings. You might use this approach if you're just getting started with the Language Model API.
@vscode/prompt-tsx - declare the prompt by using the TSX syntax.
You can use the prompt-tsx library if you want more control over how the language model prompt is composed. For example, the library can help with dynamically adapting the length of the prompt to each language model's context window size. Learn more about @vscode/prompt-tsx or explore the chat extension sample to get started.

To learn more about the concepts of prompt engineering, we suggest reading OpenAI's excellent Prompt engineering guidelines.

Tip: take advantage of the rich VS Code extension API to get the most relevant context and include it in your prompt. For example, to include the contents of the active file in the editor.

Use the LanguageModelChatMessage class
The Language Model API provides the LanguageModelChatMessage class to represent and create chat messages. You can use the LanguageModelChatMessage.User or LanguageModelChatMessage.Assistant methods to create user or assistant messages respectively.

In the following example, the first message provides context for the prompt:

The persona used by the model in its replies (in this case, a cat)
The rules the model should follow when generating responses (in this case, explaining computer science concepts in a funny manner by using cat metaphors)
The second message then provides the specific request or instruction coming from the user. It determines the specific task to be accomplished, given the context provided by the first message.

TypeScript

const craftedPrompt = [
  vscode.LanguageModelChatMessage.User(
    'You are a cat! Think carefully and step by step like a cat would. Your job is to explain computer science concepts in the funny manner of a cat, using cat metaphors. Always start your response by stating what concept you are explaining. Always include code samples.'
  ),
  vscode.LanguageModelChatMessage.User('I want to understand recursion')
];
Send the language model request
Once you've built the prompt for the language model, you first select the language model you want to use with the selectChatModels method. This method returns an array of language models that match the specified criteria. If you are implementing a chat participant, we recommend that you instead use the model that is passed as part of the request object in your chat request handler. This ensures that your extension respects the model that the user chose in the chat model dropdown. Then, you send the request to the language model by using the sendRequest method.

To select the language model, you can specify the following properties: vendor, id, family, or version. Use these properties to either broadly match all models of a given vendor or family, or select one specific model by its ID. Learn more about these properties in the API reference.

Note: Currently, gpt-4o, gpt-4o-mini, o1, o1-mini, claude-3.5-sonnet are supported for the language model family. If you are unsure what model to use, we recommend gpt-4o for it's performance and quality. For interactions directly in the editor, we recommend gpt-4o-mini for it's performance.

If there are no models that match the specified criteria, the selectChatModels method returns an empty array. Your extension must appropriately handle this case.

The following example shows how to select all Copilot models, regardless of the family or version:

TypeScript

const models = await vscode.lm.selectChatModels({
  vendor: 'copilot'
});

// No models available
if (models.length === 0) {
  // TODO: handle the case when no models are available
}
Important: Copilot's language models require consent from the user before an extension can use them. Consent is implemented as an authentication dialog. Because of that, selectChatModels should be called as part of a user-initiated action, such as a command.

After you select a model, you can send a request to the language model by invoking the sendRequest method on the model instance. You pass the prompt you crafted earlier, along with any additional options, and a cancellation token.

When you make a request to the Language Model API, the request might fail. For example, because the model doesn't exist, or the user didn't give consent to use the Language Model API, or because quota limits are exceeded. Use LanguageModelError to distinguish between different types of errors.

The following code snippet shows how to make a language model request:

TypeScript

try {
  const [model] = await vscode.lm.selectChatModels({ vendor: 'copilot', family: 'gpt-4o' });
  const request = model.sendRequest(craftedPrompt, {}, token);
} catch (err) {
  // Making the chat request might fail because
  // - model does not exist
  // - user consent not given
  // - quota limits were exceeded
  if (err instanceof vscode.LanguageModelError) {
    console.log(err.message, err.code, err.cause);
    if (err.cause instanceof Error && err.cause.message.includes('off_topic')) {
      stream.markdown(
        vscode.l10n.t("I'm sorry, I can only explain computer science concepts.")
      );
    }
  } else {
    // add other error handling logic
    throw err;
  }
}
Interpret the response
After you've sent the request, you have to process the response from the language model API. Depending on your usage scenario, you can pass the response directly on to the user, or you can interpret the response and perform extra logic.

The response (LanguageModelChatResponse) from the Language Model API is streaming-based, which enables you to provide a smooth user experience. For example, by reporting results and progress continuously when you use the API in combination with the Chat API.

Errors might occur while processing the streaming response, such as network connection issues. Make sure to add appropriate error handling in your code to handle these errors.

The following code snippet shows how an extension can register a command, which uses the language model to change all variable names in the active editor with funny cat names. Notice that the extension streams the code back to the editor for a smooth user experience.

TypeScript

vscode.commands.registerTextEditorCommand(
  'cat.namesInEditor',
  async (textEditor: vscode.TextEditor) => {
    // Replace all variables in active editor with cat names and words

    const [model] = await vscode.lm.selectChatModels({
      vendor: 'copilot',
      family: 'gpt-4o'
    });
    let chatResponse: vscode.LanguageModelChatResponse | undefined;

    const text = textEditor.document.getText();

    const messages = [
      vscode.LanguageModelChatMessage
        .User(`You are a cat! Think carefully and step by step like a cat would.
        Your job is to replace all variable names in the following code with funny cat variable names. Be creative. IMPORTANT respond just with code. Do not use markdown!`),
      vscode.LanguageModelChatMessage.User(text)
    ];

    try {
      chatResponse = await model.sendRequest(
        messages,
        {},
        new vscode.CancellationTokenSource().token
      );
    } catch (err) {
      if (err instanceof vscode.LanguageModelError) {
        console.log(err.message, err.code, err.cause);
      } else {
        throw err;
      }
      return;
    }

    // Clear the editor content before inserting new content
    await textEditor.edit(edit => {
      const start = new vscode.Position(0, 0);
      const end = new vscode.Position(
        textEditor.document.lineCount - 1,
        textEditor.document.lineAt(textEditor.document.lineCount - 1).text.length
      );
      edit.delete(new vscode.Range(start, end));
    });

    try {
      // Stream the code into the editor as it is coming in from the Language Model
      for await (const fragment of chatResponse.text) {
        await textEditor.edit(edit => {
          const lastLine = textEditor.document.lineAt(textEditor.document.lineCount - 1);
          const position = new vscode.Position(lastLine.lineNumber, lastLine.text.length);
          edit.insert(position, fragment);
        });
      }
    } catch (err) {
      // async response stream may fail, e.g network interruption or server side error
      await textEditor.edit(edit => {
        const lastLine = textEditor.document.lineAt(textEditor.document.lineCount - 1);
        const position = new vscode.Position(lastLine.lineNumber, lastLine.text.length);
        edit.insert(position, (<Error>err).message);
      });
    }
  }
);
Considerations
Model availability
We don't expect specific models to stay supported forever. When you reference a language model in your extension, make sure to take a "defensive" approach when sending requests to that language model. This means that you should gracefully handle cases where you don't have access to a particular model.

Choosing the appropriate model
Extension authors can choose which model is the most appropriate for their extension. We recommend using gpt-4o for its performance and quality. To get a full list of available models, you can use this code snippet:

TypeScript

const allModels = await vscode.lm.selectChatModels(MODEL_SELECTOR);
Note
The recommended GPT-4o model has a limit of 64K tokens. The returned model object from the selectChatModels call has a maxInputTokens attribute that shows the token limit. These limits will be expanded as we learn more about how extensions are using the language models.

Rate limiting
Extensions should responsibly use the language model and be aware of rate limiting. VS Code is transparent to the user regarding how extensions are using language models and how many requests each extension is sending and how that influences their respective quotas.

Extensions should not use the Language Model API for integration tests due to rate-limitations. Internally, VS Code uses a dedicated non-production language model for simulation testing, and we are currently thinking how to provide a scalable language model testing solution for extensions.

Testing your extension
The responses that the Language Model API provides are nondeterministic, which means that you might get a different response for an identical request. This behavior can be challenging for testing your extension.

The part of the extension for building prompts and interpreting language model responses is deterministic, and can thus be unit tested without using an actual language model. However, interacting and getting responses from the language model itself, is nondeterministic and can’t be easily tested. Consider designing your extension code in a modular way to enable you to unit test the specific parts that can be tested.

Publishing your extension
Once you have created your AI extension, you can publish your extension to the Visual Studio Marketplace:

Before publishing to the VS Marketplace we recommend that you read the Microsoft AI tools and practices guidelines. These guidelines provide best practices for the responsible development and use of AI technologies.
By publishing to the VS Marketplace, your extension is adhering to the GitHub Copilot extensibility acceptable development and use policy.
If your extension already contributes functionality other than using the Language Model API, we recommend that you do not introduce an extension dependency on GitHub Copilot in the extension manifest. This ensures that extension users that do not use GitHub Copilot can use the non language model functionality without having to install GitHub Copilot. Make sure to have appropriate error handling when accessing language models for this case.
Upload to the Marketplace as described in Publishing Extension.
Related content
Language Models API Reference
Learn more about @vscode/prompt-tsx
Build a VS Code chat extension



Craft language model prompts
You can build language model prompts by using string concatenation, but it's hard to compose features and make sure your prompts stay within the context window of language models. To overcome these limitations, you can use the @vscode/prompt-tsx library.

The @vscode/prompt-tsx library provides the following features:

TSX-based prompt rendering: Compose prompts using TSX components, making them more readable and maintainable
Priority-based pruning: Automatically prune less important parts of prompts to fit within the model's context window
Flexible token management: Use properties like flexGrow, flexReserve, and flexBasis to cooperatively use token budgets
Tool integration: Integrate with VS Code's language model tools API
For a complete overview of all features and detailed usage instructions, refer to the full README.

This article describes practical examples of prompt design with the library. The complete code for these examples can be found in the prompt-tsx repository.

Manage priorities in the conversation history
Including conversation history in your prompt is important as it enables the user to ask follow-up questions to previous messages. However, you want to make sure its priority is treated appropriately because history can grow large over time. We've found that the pattern which makes the most sense is usually to prioritize, in order:

The base prompt instructions
The current user query
The last couple of turns of chat history
Any supporting data
As much of the remaining history as you can fit
For this reason, split the history into two parts in the prompt, where recent prompt turns are prioritized over general contextual information.

In this library, each TSX node in the tree has a priority that is conceptually similar to a zIndex where a higher number means a higher priority.

Step 1: Define the HistoryMessages component
To list history messages, define a HistoryMessages component. This example provides a good starting point, but you might have to expand it if you deal with more complex data types.

This example uses the PrioritizedList helper component, which automatically assigns ascending or descending priorities to each of its children.

Tsx

import {
	UserMessage,
	AssistantMessage,
	PromptElement,
	BasePromptElementProps,
	PrioritizedList,
} from '@vscode/prompt-tsx';
import { ChatContext, ChatRequestTurn, ChatResponseTurn, ChatResponseMarkdownPart } from 'vscode';

interface IHistoryMessagesProps extends BasePromptElementProps {
	history: ChatContext['history'];
}

export class HistoryMessages extends PromptElement<IHistoryMessagesProps> {
	render(): PromptPiece {
		const history: (UserMessage | AssistantMessage)[] = [];
		for (const turn of this.props.history) {
			if (turn instanceof ChatRequestTurn) {
				history.push(<UserMessage>{turn.prompt}</UserMessage>);
			} else if (turn instanceof ChatResponseTurn) {
				history.push(
					<AssistantMessage name={turn.participant}>
						{chatResponseToMarkdown(turn)}
					</AssistantMessage>
				);
			}
		}
		return (
			<PrioritizedList priority={0} descending={false}>
				{history}
			</PrioritizedList>
		);
	}
}
Step 2: Define the Prompt component
Next, define a MyPrompt component that includes the base instructions, user query, and history messages with their appropriate priorities. Priority values are local among siblings. Remember that you might want to trim older messages in the history before touching anything else in the prompt, so you need to split up two <HistoryMessages> elements:

Tsx

import {
	UserMessage,
	PromptElement,
	BasePromptElementProps,
} from '@vscode/prompt-tsx';

interface IMyPromptProps extends BasePromptElementProps {
	history: ChatContext['history'];
	userQuery: string;
}

export class MyPrompt extends PromptElement<IMyPromptProps> {
	render() {
		return (
			<>
				<UserMessage priority={100}>
					Here are your base instructions. They have the highest priority because you want to make
					sure they're always included!
				</UserMessage>
				{/* Older messages in the history have the lowest priority since they're less relevant */}
				<HistoryMessages history={this.props.history.slice(0, -2)} priority={0} />
				{/* The last 2 history messages are preferred over any workspace context you have below */}
				<HistoryMessages history={this.props.history.slice(-2)} priority={80} />
				{/* The user query is right behind the based instructions in priority */}
				<UserMessage priority={90}>{this.props.userQuery}</UserMessage>
				<UserMessage priority={70}>
					With a slightly lower priority, you can include some contextual data about the workspace
					or files here...
				</UserMessage>
			</>
		);
	}
}
Now, all older history messages are pruned before the library tries to prune other elements of the prompt.

Step 3: Define the History component
To make consumption a little easier, define a History component that wraps the history messages and uses the passPriority attribute to act as a pass-through container. With passPriority, its children are treated as if they are direct children of the containing element for prioritization purposes.

Tsx

import { PromptElement, BasePromptElementProps } from '@vscode/prompt-tsx';

interface IHistoryProps extends BasePromptElementProps {
	history: ChatContext['history'];
	newer: number; // last 2 message priority values
	older: number; // previous message priority values
	passPriority: true; // require this prop be set!
}

export class History extends PromptElement<IHistoryProps> {
	render(): PromptPiece {
		return (
			<>
				<HistoryMessages history={this.props.history.slice(0, -2)} priority={this.props.older} />
				<HistoryMessages history={this.props.history.slice(-2)} priority={this.props.newer} />
			</>
		);
	}
}
Now, you can use and reuse this single element to include chat history:

Tsx

<History history={this.props.history} passPriority older={0} newer={80}/>
Grow file contents to fit
In this example, you want to include the contents of all files the user is currently looking at in their prompt. These files could be large, to the point where including all of them would lead to their text being pruned! This example shows how to use the flexGrow property to cooperatively size the file contents to fit within the token budget.

Step 1: Define base instructions and user query
First, you define a UserMessage component that includes the base instructions.

Tsx

<UserMessage priority={100}>Here are your base instructions.</UserMessage>
You then include the user query by using the UserMessage component. This component has a high priority to ensure it is included right after the base instructions.

Tsx

<UserMessage priority={90}>{this.props.userQuery}</UserMessage>
Step 2: Include the File Contents
You can now include the file contents by using the FileContext component. You assign it a flexGrow value of 1 to ensure it is rendered after the base instructions, user query, and history.

Tsx

<FileContext priority={70} flexGrow={1} files={this.props.files} />
With a flexGrow value, the element gets any unused token budget in its PromptSizing object that's passed into its render() and prepare() calls. You can read more about the behavior of flex elements in the prompt-tsx documentation.

Step 3: Include the history
Next, include the history messages using the History component that you created previously. This is a little trickier, since you do want some history to be shown, but also want the file contents to take up most the prompt.

Therefore, assign the History component a flexGrow value of 2 to ensure it is rendered after all other elements, including <FileContext />. But, also set a flexReserve value of "/5" to reserve 1/5th of the total budget for history.

Tsx

<History
	history={this.props.history}
	passPriority
	older={0}
	newer={80}
	flexGrow={2}
	flexReserve="/5"
/>
Step 3: Combine all elements of the prompt
Now, combine all the elements into the MyPrompt component.

Tsx

import {
	UserMessage,
	PromptElement,
	BasePromptElementProps,
} from '@vscode/prompt-tsx';
import { History } from './history';

interface IFilesToInclude {
	document: TextDocument;
	line: number;
}

interface IMyPromptProps extends BasePromptElementProps {
	history: ChatContext['history'];
	userQuery: string;
	files: IFilesToInclude[];
}

export class MyPrompt extends PromptElement<IMyPromptProps> {
	render() {
		return (
			<>
				<UserMessage priority={100}>Here are your base instructions.</UserMessage>
				<History
					history={this.props.history}
					passPriority
					older={0}
					newer={80}
					flexGrow={2}
					flexReserve="/5"
				/>
				<UserMessage priority={90}>{this.props.userQuery}</UserMessage>
				<FileContext priority={70} flexGrow={1} files={this.props.files} />
			</>
		);
	}
}
Step 4: Define the FileContext component
Finally, define a FileContext component that includes the contents of the files the user is currently looking at. Because you used flexGrow, you can implement logic that gets as many of the lines around the 'interesting' line for each file by using the information in PromptSizing.

For brevity, the implementation logic for getExpandedFiles is omitted. You can check it out in the prompt-tsx repo.

Tsx

import { PromptElement, BasePromptElementProps, PromptSizing, PromptPiece } from '@vscode/prompt-tsx';

class FileContext extends PromptElement<{ files: IFilesToInclude[] } & BasePromptElementProps> {
	async render(_state: void, sizing: PromptSizing): Promise<PromptPiece> {
		const files = await this.getExpandedFiles(sizing);
		return <>{files.map(f => f.toString())}</>;
	}

	private async getExpandedFiles(sizing: PromptSizing) {
		// Implementation details are summarized here.
		// Refer to the repo for the complete implementation.
	}
}
Summary
In these examples, you created a MyPrompt component that includes base instructions, user query, history messages, and file contents with different priorities. You used flexGrow to cooperatively size the file contents to fit within the token budget.

By following this pattern, you can ensure that the most important parts of your prompt are always included, while less important parts are pruned as needed to fit within the model's context window. For the complete implementation details of the getExpandedFiles method and the FileContextTracker class, refer to the prompt-tsx repo.


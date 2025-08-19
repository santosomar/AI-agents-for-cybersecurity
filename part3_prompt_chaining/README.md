# Part 3: Prompt Chaining Examples

This directory contains examples demonstrating various prompt chaining techniques using LangChain Expression Language (LCEL). These examples showcase how to build sophisticated workflows for cybersecurity tasks by connecting different language model calls and processing steps.

## Files

### 1. `basic_chain_example1.py`

*   **Purpose**: Demonstrates a fundamental LCEL chain.
*   **Functionality**:
    *   Initializes a `ChatOpenAI` model (`gpt-5-mini`).
    *   Uses a `ChatPromptTemplate` to instruct an AI (as an 'ethical hacker') to provide a specified number of techniques and tools for a given topic.
    *   Includes custom processing steps using `RunnableLambda`:
        *   `uppercase_output`: Converts the AI's string output to uppercase.
        *   `count_words`: Prepends a word count to the string output.
    *   The chain is constructed as: `prompt_template | model | StrOutputParser() | uppercase_output | count_words`.
    *   Invokes the chain with a sample topic ('scanning a web application') and a tip count (5), then prints the final processed output.

### 2. `basic_chain_security_incident_chain_example.py`

*   **Purpose**: Illustrates a multi-stage security incident analysis workflow.
*   **Functionality**:
    *   Defines multiple `ChatPromptTemplate` instances for various AI personas and analysis stages (initial assessment, threat actor analysis, impact assessment, mitigation, CISO summary, and specific incident types like malware, phishing, data breach).
    *   Uses a helper function `format_to_json` to structure analysis outputs into JSON.
    *   Constructs specialized analysis chains that output JSON.
    *   Implements conditional logic using `RunnableBranch` (`incident_specific_chain`) based on incident type classification performed by `determine_incident_type`.
    *   The `full_analysis_chain` orchestrates the entire workflow: initial analysis, incident classification, parallel execution of specialized analyses (threat, impact, mitigation, type-specific), and generation of an executive summary.
    *   Demonstrates invoking the chain with sample incident details and printing the summary and full analysis.

### 3. `branching_chains.py`

*   **Purpose**: Shows how to use `RunnableBranch` for conditional routing in a vulnerability assessment context.
*   **Functionality**:
    *   Classifies the severity of a reported vulnerability (critical, high, medium, or low) using a `classification_template`.
    *   Based on the classification, routes the input to one of four specialized sub-chains, each with a prompt template tailored to the severity level.
    *   Each sub-chain generates an appropriate response (e.g., pen test plan for critical, remediation strategy for high).
    *   Initializes a `ChatOpenAI` model (`gpt-5-mini`).
    *   Invokes the chain with an example vulnerability ("Unpatched remote code execution vulnerability in an Apache httpd web server") and prints the result.

### 4. `branching_chains_threat_hunting.py`

*   **Purpose**: Demonstrates a threat hunting workflow that adapts based on the type of indicator of compromise (IOC).
*   **Functionality**:
    *   Classifies an input IOC as IP address, domain, file hash, or behavior pattern using a `classification_template` and a helper function `determine_indicator_type`.
    *   Uses `RunnableBranch` to route the IOC to a specialized analysis path. Each path has a unique `ChatPromptTemplate` instructing an AI (as an expert threat hunter) to generate a detailed threat hunting plan specific to the IOC type.
    *   Employs `RunnableMap` to preserve the original indicator alongside its classification for use in the branched chains.
    *   Initializes a `ChatOpenAI` model (`gpt-5-mini`).
    *   Runs the chain with example IOCs of each type and prints the generated hunting plans.

### 5. `parallel_chains.py`

*   **Purpose**: Illustrates using `RunnableParallel` to execute different analysis paths concurrently for a penetration testing scenario.
*   **Functionality**:
    *   Takes a `target_system` as input.
    *   An initial prompt gathers general characteristics and potential entry points of the target.
    *   Two parallel branches are defined:
        *   **Reconnaissance Branch**: Generates a list of reconnaissance techniques and tools.
        *   **Exploitation Branch**: Suggests potential exploitation methods and tools.
    *   These branches are implemented using `RunnableLambda` functions that format specific prompts, which are then piped to the AI model.
    *   `RunnableParallel` executes these two branches.
    *   The outputs from both branches are then combined by a final `RunnableLambda` (`create_pentest_plan`) into a single penetration testing plan.
    *   Initializes a `ChatOpenAI` model (`gpt-5-mini`).
    *   Invokes the chain with an example target ("E-commerce website running in the cloud") and prints the plan.

### 6. `parallel_chains_threat_hunting.py`

*   **Purpose**: Showcases a comprehensive threat hunting workflow using `RunnableParallel` to analyze an indicator from multiple perspectives simultaneously.
*   **Functionality**:
    *   Processes a threat indicator through an `initial_assessment_chain`.
    *   Then, using `RunnableParallel`, the indicator is concurrently analyzed by four specialized branches:
        *   **Technical Analysis**: Focuses on TTPs, malware families, and technical detection methods.
        *   **Threat Context**: Gathers historical usage, associated campaigns, and geo/industry targeting.
        *   **Hunting Strategy**: Develops specific hunt queries and identifies artifacts.
        *   **Mitigation**: Recommends containment, monitoring, and long-term defense.
    *   Each branch uses a specific `ChatPromptTemplate` and is constructed as a `RunnableLambda` piped to the AI model.
    *   The results from the initial assessment and all parallel branches are combined into a `COMPREHENSIVE THREAT HUNTING REPORT` by the `create_threat_hunting_report` function, orchestrated via `RunnableLambda` and `RunnableParallel` to manage inputs.
    *   Initializes a `ChatOpenAI` model (`gpt-5-mini`).
    *   Runs the chain with example indicators and prints the detailed report.

## Common Elements

*   **`dotenv`**: Used in all scripts to load environment variables (like API keys) from a `.env` file.
*   **`ChatOpenAI`**: The primary language model interface, typically initialized with `gpt-5-mini`.
*   **`ChatPromptTemplate`**: Used to structure the input to the language model, often defining a system message (persona) and a human message (task).
*   **`StrOutputParser`**: A common output parser to convert the model's message object into a simple string.
*   **`RunnableLambda`**: Allows arbitrary Python functions to be integrated into LCEL chains.
*   **LCEL Pipe Syntax (`|`)**: The core mechanism for chaining components together.

These examples provide a solid foundation for understanding and building complex, multi-step AI-driven workflows for various cybersecurity applications.

**SECURITY NOTE**: Never commit your API keys to version control. Also, instead of using environment variables to store sensitive information, you can use a secrets management service like CyberArk Conjur, HashiCorp Vault or AWS Secrets Manager.

# LogicLM

In this LogicLM repository, we explore the possibilities of enhancing LLM performance on logical problems by making systems which combine LLMs with logical programming (LP) languages like ASP and Prolog.

To this extent, we have identified two key areas where we can leverage combined LP and LLM systems.


## Instance Generation

In the case of instance generation, we already have access to a fully written LP which can be used to classify any instance that is provided to it with matching LP facts. This can be useful if we have text-based instances which should be classified using some logical decision making process. 

To convert these text-based instances to LP facts, we use an LLM which has been instructed to identify some key facts about he instance which are required to make the final classification. These facts are returned as JSON, and subsequently turned into correctly formatted ASP code. LLMs are taught how to extract the facts via in-context learning in which we explain which facts we hope to extract and provide an example of what the output JSON should look like.

In this repository we present two use-cases.

### Lost Shipment Customer Chats

The lost shipment dataset is a synthetically generated dataset containing chat logs between two LLM agents of which one is a customer service representative from a large logistics company, and the other is a customer that is sending/recieving a shipment. The dataset closely mirrors a real dataset belonging to our industry partner which is also a large logistics company.

In each case, a package can be classified as 'still in transit', 'held at customs', or 'lost', depending on characteristics about the shipment which are revealed in the chat log.


### SaRa Dataset

The [Statutory Reasoning (SaRa) dataset](https://arxiv.org/abs/2005.05257), presented by Holzenberger et al. in 2020, contains a series instances in the form of statements and questions regarding tax law. Along with the questions, they also provide a prolog program in which all relevant tax law rules are encoded to make classifications on the instances. 

## Scheduling Program Generation

A second avenue to integrate LLMs with LP that we have explored is the writing of fully fledged ASP programs for scheduling problems. To this extent, we have created a system of LLMs which, given a correctly formatted problem specification, can create an ASP program for the problem along with an example instance.

The system is set up to take the following inputs about the problem:

    - Problem description
        A short textual description of the problem
    - Instance details
        A list of the variables that make instances unique
    - Hard constrains
        A list of hard constraints which cannot be violated
    - Soft constraints
        A list of soft constraints. These constrains can be violated but each violation will incur a penalty.

For each of these sections, a bespoke chain of prompt can help to write the required code via few shot learning with examples specific to the types of ASP rules we are looking to generate.


# Running the Code

All code can be run from the jupyter notebooks in the notebooks folder. To use them, they must first be moved out of the notebooks folder into the root folder. This is to make sure the import statements work correctly.

## 1 ASP Scheduler

Use the 1_ASP_Scheduler notebook.

All problem descriptions are imported using: 

`from ASP_Scheduler.problem_descriptions import all_problems`

From there, just input the correct problem description to the `scheduler.full_ASP_program` function


## 2 Lost Shipment Customer Chats

### Generator

The generator is used to generate a synthetic dataset of customer chats.

Use the 2_Lost_Shipment_Generator notebook.

### Classifier

The classifiers are used to classify the previously generated dataset.

Use the 2_Lost_Shipment_Classifier notebook.

## 3 SaRa Dataset


# Using Snellius

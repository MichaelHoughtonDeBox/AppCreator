#import libraries
import streamlit as st
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain import PromptTemplate
from  langchain import PromptTemplate, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from streamlit_extras.switch_page_button import switch_page

api = st.secrets["OPENAI_KEY"]

def main():
    
    if "state" not in st.session_state:
        st.session_state["state"] = "main"
    
    for variable in ['app_name', 'app_emoji', 'app_description', 'system_prompt', 'user_input_label', 'placeholder']:
        if variable not in st.session_state:
            st.session_state[variable] = ''
        
    st.title("Streamlit Chatbot Maker🤯")
    st.markdown("Welcome to the future of app creation! This is an LLM-Powered platform that effortlessly crafts other LLM-Powered applications.")

    app_user_input = st.text_area(label= "Describe the app you need below: ", key= "appinput",
            placeholder="Eg. An app that tells gives me Youtube video ideas about a given topic...")

    if st.button("Create"):
        
        app_system_prompt = """You are streamlitGPT your job is to help a user generate a simple LLM streamlit app. The user will describe to you what the application will do. You will then take that description and generate a Fun Name, an emoji for the app, an app description, and the system prompt for the LLM. You will use this exact format as shown below for the variables. 

        Your output should be a python dictionary only include these variables and nothing else. Output it as python code. 

        'app_name': "The name of the app should go here as a string, always add emojis",
        'app_emoji': "The emjoi that best suits the app name should go here",
        'app_description': "A description of the app should go here as a string. be fun and witty",
        'system_prompt': "You are a chatbot called [name of app here] that helps the human with [describe what the app will do]. Your job is to do [give it its role].\nChat History: [add input variable called chat_history delimited by curly brakets] \nUser Question: [add an input variable called question delimited by curly brakets]",
        'user_input_label': "[add a label for the input box here]",
        'placeholder': "Create a placeholder for the question input box, this should be a relevant example user input",
        
        {app_question}
        """
        custom_prompt1 = PromptTemplate(template=app_system_prompt, input_variables=["app_question"])

        chain1 = LLMChain(
        llm = ChatOpenAI (
            temperature=0.2, 
            model_name="gpt-3.5-turbo",
            openai_api_key=api,
            ),
        prompt=custom_prompt1,
        verbose="False",
        ) 

        app_output_str = chain1.run(app_question=app_user_input, return_only_outputs=True)
        app_output = ast.literal_eval(app_output_str)
        
        st.session_state.app_name = app_output['app_name']
        st.session_state.app_emoji = app_output['app_emoji']
        st.session_state.app_description = app_output['app_description']
        st.session_state.system_prompt = app_output['system_prompt']
        st.session_state.user_input_label = app_output['user_input_label']
        st.session_state.placeholder = app_output['placeholder']
        
        # Change the state variable after the variables have been stored
        st.session_state["state"] = "created"
        
        st.experimental_rerun()
  
def created():
    # Check the value of the state variable
    if st.session_state["state"] == "created":
        
        if "generated" not in st.session_state:
            st.session_state["generated"] = []

        if "past" not in st.session_state:
            st.session_state["past"] = []

        st.title(st.session_state.app_name)
        st.markdown(f"{st.session_state.app_emoji} {st.session_state.app_description}")

        if "memory" not in st.session_state:
                st.session_state["memory"] = ConversationBufferMemory(memory_key="chat_history", input_key= "question")

        user_input = st.text_input(label=st.session_state.user_input_label, placeholder=st.session_state.placeholder)

        if st.button("Enter"):
                            
            custom_prompt2 = PromptTemplate(template=st.session_state.system_prompt, input_variables=["question", "chat_history"])

            chain2 = LLMChain(
            llm = ChatOpenAI (
                temperature=0.5, 
                model_name="gpt-3.5-turbo",
                openai_api_key=api,
                ),
            prompt=custom_prompt2,
            verbose="False",
            memory = st.session_state.memory
            ) 
            
            output = chain2.run(question=user_input, chat_history = st.session_state["memory"], return_only_outputs=True)
            
            st.session_state.past.append(user_input)
            st.session_state.generated.append(output)

            st.markdown(output)
            
            if st.session_state["generated"]:
                with st.expander("See Chat History"):
                    #st.markdown(st.session_state["generated"])
                    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
                        st.markdown(st.session_state["past"][i])
                        st.markdown(st.session_state["generated"][i])
            
        # if st.button("Start Over"):
        #     # Set the state variable back to "main"
        #     st.session_state["state"] = "main"
        #     for variable in ['app_name', 'app_emoji', 'app_description', 'system_prompt', 'user_input_label', 'placeholder']:
        #         st.session_state[variable] = ''
        #     for variable in ['generated', 'past']:
        #         st.session_state[variable] = []
        #     # Force Streamlit to rerun the script
        #     st.experimental_rerun()

def app():
    if st.session_state.get("state", "main") == "main":
        main()
    elif st.session_state["state"] == "created":
        created()

if __name__ == "__main__":
    app()

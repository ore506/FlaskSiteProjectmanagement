
import os
import openai
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts  import ChatPromptTemplate
from langchain.output_parsers import (CommaSeparatedListOutputParser, DatetimeOutputParser)
from langchain_community.document_loaders import PyPDFLoader
import copy
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from bidi.algorithm import get_display


from langchain.globals import set_verbose


class OpenTool:
    def __init__(self):
        arr =os.environ.items()
        for key,value in arr:
            if key == 'OPENAI_API_KEY':
                print (f"{key}:{value}")
        openai.api_key = os.getenv('OPENAI_API_KEY')
        print(openai.api_key)
        client =openai.OpenAI()
        self.openClient = client
        print("int")

    def createCall(self):
        openClientV=self.openClient
        completion = openClientV.chat.completions.create(model = 'gpt-4',
                                                         messages = [{'role':'system','content':'''You are cheti, a finance assitent answer questions with sarcastic responses'''}],
                                                         max_tokens=250,
                                                         temperature=0.5,
                                                         seed=365,
                                                         stream=True)
        for i in completion:
            print(i.choices[0].delta.content,end = "")

    def createCallWithTemp(self):
        list_instractions = CommaSeparatedListOutputParser().get_format_instructions()
        chat_template = ChatPromptTemplate.from_messages([('human',"When Nvidia stock reported?{year}. please provide next dates? \n" +list_instractions)])

        print(chat_template.messages[0].prompt.template)


        chat = ChatOpenAI(model_name = 'gpt-4',
                            seed=365,
                            temperature=0,
                            max_tokens=100)

        list_output_parser = CommaSeparatedListOutputParser()

        chat_template_result = chat_template.invoke({'year':'2025'})

        chat_result = chat.invoke(chat_template_result)

        list_output_parser.invoke(chat_result)

        #Or we can use chain to combine all the steps

        chain = chat_template |chat | list_output_parser

        chain_result = chain.invoke({'year':'2025'})
        print (chain_result)
        return chain_result

    def createCallWithTempPipe(self):
        chat_template = ChatPromptTemplate.from_messages([('human',"When {stock} stock reported?{year}. please provide next dates? ")])

        chat = ChatOpenAI(model_name = 'gpt-4',
                            seed=365,
                            temperature=0,
                            max_tokens=100) 

        chain = chat_template | chat | DatetimeOutputParser()

        chain_result = chain.invoke({'year':'2025','stock':'Nvidia'})

        #Or in order to run in paralell we can use batch

        chain.batch([{'year':'2025','stock':'Nvidia'},{'year':'2024','stock':'Tesla'}])

    def embedPDF(self,fileName,folderPath):
        loader_pdf = PyPDFLoader(fileName)

        pages_pdf = loader_pdf.load()

        #to remove new line sign
        for i in  range (len(pages_pdf)):
            pages_pdf[i].page_content = ' '.join(pages_pdf[i].page_content.split())

        pages_pdf[0].page_content

        len(pages_pdf[0].page_content)


        #Splitting the Document into Chunks
        char_splitter = CharacterTextSplitter(separator=".", 
                                            chunk_size=700, 
                                            chunk_overlap =10)

        pages_char_split = char_splitter.split_documents(pages_pdf)
        len(pages_char_split)
        
        embedder = OpenAIEmbeddings(model="text-embedding-ada-002")
        ventorStore = Chroma.from_documents(documents=  pages_char_split, 
                                    embedding = embedder,
                                    persist_directory = folderPath)
    

    def embedWORD(self,fileName,folderPath):
        loader_word = Docx2txtLoader(fileName)

        pages_word = loader_word.load()

        #to remove new line sign
        for i in  range (len(pages_word)):
            pages_word[i].page_content = ' '.join(pages_word[i].page_content.split())

        pages_word[0].page_content

        len(pages_word[0].page_content)


        #Splitting the Document into Chunks
        char_splitter = CharacterTextSplitter(separator=".", 
                                            chunk_size=700, 
                                            chunk_overlap =10)

        pages_char_split = char_splitter.split_documents(pages_word)
        len(pages_char_split)
        
        embedder = OpenAIEmbeddings(model="text-embedding-ada-002")
        ventorStore = Chroma.from_documents(documents=  pages_char_split, 
                                    embedding = embedder,
                                    persist_directory = folderPath)
        
    
    def getIDsData(self,folderPath):
        embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
        vectorestore_from_directory = Chroma(persist_directory = folderPath, 
                                     embedding_function = embedding)
        print(f"Total stored embeddings: {vectorestore_from_directory._collection.count()}")
        all_ids = vectorestore_from_directory._collection.get(include=[])
        print(f"Available IDs: {all_ids['ids']}")
        return all_ids


    def raiseQuestion(self,folderPath,question):
        embedding = OpenAIEmbeddings(model="text-embedding-ada-002")

        vectorstore = Chroma(persist_directory = folderPath, 
                            embedding_function = embedding)
        retriver =  vectorstore.as_retriever(search_type ='mmr',
                                            search_kwargs = {'k':3,
                                                            'lambda_mult':0.7})

        TEMPLATE = '''
        Answer the following question: 
        {question}

        To answer the question, use only the following context:
        {context}

        At the end of the response,specify the name on the lecture this context is taken  from in the context:
        Resource: *property name*
        where *property name* should be substituted with the title of all resource lectures.
        '''

        prompt_template = PromptTemplate.from_template(TEMPLATE)
        chat = ChatOpenAI(model_name = 'gpt-4',
                            seed=365,
                            temperature=0,
                            max_tokens=250)

        #question ='what software do data scientists use?'

        chain = ({'context':retriver, 'question':RunnablePassthrough()}|
                                                                prompt_template |
                                                                chat |
                                                                StrOutputParser() )
        response =chain.invoke(question)
        print (response)
        return response
   


if __name__ == "__main__":
    arr =os.environ.items()
    for key,value in arr:
        if key == 'OPENAI_API_KEY':
            print (f"{key}:{value}")

    openai.api_key = os.getenv('OPENAI_API_KEY')
    print("The Key is:",openai.api_key)
    inst1=OpenTool()
    #inst1.embedPDF("Introduction_to_Data_and_Data_Science.pdf","./inv-files1")
    #inst1.embedWORD("23march.docx","./inv-files1")
    #ds_ids= inst1.getData("./ds-files")
    #print(f"Available IDs: {ds_ids['ids']}")

    inst1.raiseQuestion("./inv-files1","comprare AMD to Tesla performance")
    #print ("מה השם של הנכס?")
    #print(get_display("מה השם של הנכס?"))
    
    # print ("Vector id:",vectorestore_from_directory)
    # print(vectorestore_from_directory.get(ids= "071a2c91-da45-4b8f-9f0f-71cde9a4735f"))

      #inst1.createCallWithTempPipe()
#      #inst1.createCall()
#      inst1.createCallWithTemp()




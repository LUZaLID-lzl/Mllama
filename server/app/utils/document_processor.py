# -*- coding: utf-8 -*-
import os
from typing import List, Dict, Any
import docx2txt
import pdfplumber
import markdown
import frontmatter
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=[
                "\n\n",  # 段落
                "\n# ", "\n## ", "\n### ",  # Markdown 标题
                "\n问题:", "\n问题：",  # 问题标记
                "\n回答:", "\n回答：",  # 回答标记
                "。\n", "？\n", "！\n",  # 中文段落终止符
                "。", "？", "！",  # 中文标点
                "；\n", "：\n",  # 中文段落分隔符
                ".\n", "?\n", "!\n",  # 英文段落终止符
                ". ", "? ", "! ",  # 英文标点
            ]
        )
        
        # Markdown 转换器
        self.md = markdown.Markdown(extensions=['extra', 'toc'])
    
    def read_txt(self, file_path: str) -> str:
        """读取文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def read_pdf(self, file_path: str) -> str:
        """读取PDF文件"""
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text())
        return "\n".join(text)
    
    def read_docx(self, file_path: str) -> str:
        """读取DOCX文件"""
        return docx2txt.process(file_path)
    
    def read_markdown(self, file_path: str) -> Dict[str, Any]:
        """读取Markdown文件"""
        # 解析 frontmatter 和内容
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # 转换 Markdown 为 HTML
        html = self.md.convert(post.content)
        
        # 使用 BeautifulSoup 提取纯文本
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        return {
            'content': text,
            'metadata': post.metadata
        }
    
    def process_qa_format(self, text: str, metadata: Dict = None) -> List[Dict[str, str]]:
        """处理问答格式文本"""
        qa_pairs = []
        current_question = None
        current_answer = []
        current_metadata = {}
        
        # 处理元数据
        if metadata:
            current_metadata = metadata.copy()
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # 处理问题行
            if line.startswith(('问题:', '问题：', 'Q:', 'Question:')):
                # 保存前一个QA对
                if current_question and current_answer:
                    qa_pairs.append({
                        'question': current_question,
                        'answer': '\n'.join(current_answer),
                        'metadata': current_metadata
                    })
                # 提取问题文本
                for prefix in ['问题:', '问题：', 'Q:', 'Question:']:
                    if line.startswith(prefix):
                        current_question = line[len(prefix):].strip()
                        break
                current_answer = []
            
            # 处理答案行
            elif line.startswith(('回答:', '回答：', 'A:', 'Answer:')):
                for prefix in ['回答:', '回答：', 'A:', 'Answer:']:
                    if line.startswith(prefix):
                        answer_text = line[len(prefix):].strip()
                        if answer_text:
                            current_answer.append(answer_text)
                        break
            
            # 处理其他行（作为答案的一部分）
            elif current_answer is not None:
                current_answer.append(line)
        
        # 添加最后一个QA对
        if current_question and current_answer:
            qa_pairs.append({
                'question': current_question,
                'answer': '\n'.join(current_answer),
                'metadata': current_metadata
            })
        
        return qa_pairs
    
    def process_content(self, content: str, metadata: Dict = None) -> List[Dict[str, str]]:
        """处理文档内容，支持问答格式和普通文档"""
        # 首先尝试作为问答格式处理
        qa_pairs = self.process_qa_format(content, metadata)
        if qa_pairs:
            return qa_pairs
            
        # 如果不是问答格式，则作为普通文档处理
        return self.process_general_content(content, metadata)
    
    def process_general_content(self, content: str, metadata: Dict = None) -> List[Dict[str, str]]:
        """处理普通文档内容"""
        sections = []
        current_title = ""
        current_content = []
        current_metadata = metadata.copy() if metadata else {}
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检测标题行
            if line.startswith(('#', '第', '一、', '二、', '1.', '2.')):
                # 保存前一个部分
                if current_content:
                    sections.append({
                        'title': current_title or '概述',
                        'content': '\n'.join(current_content),
                        'metadata': current_metadata
                    })
                    current_content = []
                
                current_title = line.lstrip('#').strip()
            else:
                current_content.append(line)
        
        # 保存最后一个部分
        if current_content:
            sections.append({
                'title': current_title or '概述',
                'content': '\n'.join(current_content),
                'metadata': current_metadata
            })
        
        # 如果没有找到任何分节，将整个文档作为一个部分
        if not sections:
            sections.append({
                'title': metadata.get('title', '文档概述') if metadata else '文档概述',
                'content': content.strip(),
                'metadata': current_metadata
            })
        
        return sections
    
    def create_documents(self, sections: List[Dict[str, str]]) -> List[Document]:
        """创建文档对象，支持问答对和普通文档"""
        documents = []
        for section in sections:
            # 处理问答对格式
            if 'question' in section:
                doc_text = f"问题: {section['question']}\n回答: {section['answer']}"
                doc_type = 'qa_pair'
                title = section['question']
            # 处理普通文档格式
            else:
                doc_text = f"标题: {section['title']}\n内容: {section['content']}"
                doc_type = 'knowledge'
                title = section['title']
            
            # 构建元数据
            metadata = {
                'type': doc_type,
                'title': title
            }
            if 'metadata' in section:
                metadata.update(section['metadata'])
            
            documents.append(Document(
                page_content=doc_text,
                metadata=metadata
            ))
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档"""
        return self.text_splitter.split_documents(documents)
    
    def process_file(self, file_path: str) -> List[Document]:
        """处理单个文件"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            metadata = {
                'source': file_path,
                'file_type': file_ext[1:] if file_ext else 'unknown'
            }
            
            # 读取文件内容
            if file_ext == '.txt':
                content = self.read_txt(file_path)
            elif file_ext == '.pdf':
                content = self.read_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                content = self.read_docx(file_path)
            elif file_ext in ['.md', '.markdown']:
                result = self.read_markdown(file_path)
                content = result['content']
                metadata.update(result['metadata'])
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 处理文档内容
            sections = self.process_content(content, metadata)
            
            # 创建文档
            documents = self.create_documents(sections)
            
            # 分割文档
            return self.split_documents(documents)
            
        except Exception as e:
            raise Exception(f"处理文件 {file_path} 失败: {str(e)}") 
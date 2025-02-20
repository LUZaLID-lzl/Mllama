#### **1. 准备环境**

- 安装依赖库（以PyTorch和Hugging Face生态为例）：
    
    ```bash
    pip install torch transformers datasets accelerate peft bitsandbytes
    ```
    
- 确保CUDA驱动和PyTorch版本兼容。

#### **2. 加载模型和Tokenizer**

- 从Hugging Face或本地加载模型：
    
    ```python
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    model_name = "deepseek-ai/deepseek-r1"  # 替换为实际模型路径
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",  # 自动分配GPU/CPU
        torch_dtype=torch.bfloat16  # 节省显存
    )
    ```
    

#### **3. 准备数据集**

- 数据集格式应为文本文件（如JSON、CSV或纯文本），每条样本对应一个输入-输出对。
- 使用 `datasets` 库加载数据：
    
    ```python
    from datasets import load_dataset
    
    dataset = load_dataset("json", data_files="your_data.json")
    ```
    

#### **4. 数据预处理**

- 将文本转换为模型可接受的输入格式（如添加特殊标记、截断/填充）：
    
    ```python
    def preprocess_function(examples):
        inputs = [f"Instruction: {x}\nResponse: " for x in examples["instruction"]]
        model_inputs = tokenizer(
            inputs,
            max_length=512,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        return model_inputs
    
    tokenized_dataset = dataset.map(preprocess_function, batched=True)
    ```
    

#### **5. 配置训练参数**

- 使用 `TrainingArguments` 定义训练参数：
    
    ```python
    from transformers import TrainingArguments
    
    training_args = TrainingArguments(
        output_dir="./results",
        per_device_train_batch_size=4,  # 根据显存调整
        gradient_accumulation_steps=8,   # 显存不足时增大此值
        learning_rate=2e-5,
        num_train_epochs=3,
        logging_dir="./logs",
        save_strategy="epoch",
        fp16=True,  # 使用混合精度训练（A100可用bf16）
    )
    ```
    

#### **6. 选择高效微调方法（可选）**

- 使用 **LoRA**（低秩适配）减少显存占用：
    
    ```python
    from peft import LoraConfig, get_peft_model
    
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],  # 针对模型的注意力层
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()  # 查看可训练参数量
    ```
    

#### **7. 开始训练**

- 使用 `Trainer` 启动训练：
    
    ```python
    from transformers import Trainer
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
    )
    
    trainer.train()
    ```
    

#### **8. 保存和测试模型**

- 保存微调后的模型：
    
    ```python
    model.save_pretrained("./fine-tuned-model")
    tokenizer.save_pretrained("./fine-tuned-model")
    ```
    
- 测试生成效果：
    

```python
input_text = "Instruction: 写一首关于春天的诗\nResponse: "
inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_length=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```


### **注意事项**

1. **显存优化**：
    
    - 使用 `bitsandbytes` 进行4/8-bit量化：
        
        ```python
        model = AutoModelForCausalLM.from_pretrained(model_name, load_in_4bit=True)
        ```
        
    - 梯度累积（`gradient_accumulation_steps`）和梯度检查点（`gradient_checkpointing=True`）。
2. **数据集质量**：
    
    - 确保数据与目标任务相关，且格式与模型预训练数据相似。
3. **监控训练**：
    
    - 使用 `tensorboard` 或 `wandb` 监控损失和指标。


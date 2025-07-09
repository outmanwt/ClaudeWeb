from datetime import datetime
import re

class TemplateGenerator:
    def __init__(self):
        self.templates = {
            '刷题': self.generate_quiz_template,
            '考试': self.generate_quiz_template,
            '题目': self.generate_quiz_template,
            '计算器': self.generate_calculator_template,
            '工具': self.generate_calculator_template,
            'calculator': self.generate_calculator_template,
            'hello': self.generate_hello_template,
            '测试': self.generate_hello_template,
            '默认': self.generate_hello_template
        }
    
    def generate_template(self, project_name: str, user_prompt: str) -> str:
        """根据关键词选择合适的模板"""
        user_prompt_lower = user_prompt.lower()
        
        # 检查关键词匹配
        for keyword, generator in self.templates.items():
            if keyword in user_prompt_lower:
                return generator(project_name, user_prompt)
        
        # 默认使用hello模板
        return self.generate_hello_template(project_name, user_prompt)
    
    def generate_quiz_template(self, project_name: str, user_prompt: str) -> str:
        """生成刷题系统模板"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - 在线刷题系统</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 800px;
            width: 90%;
            padding: 30px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
        }}
        
        .quiz-container {{
            margin: 30px 0;
        }}
        
        .question {{
            font-size: 1.3rem;
            color: #333;
            margin-bottom: 20px;
            line-height: 1.5;
        }}
        
        .options {{
            display: grid;
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .option {{
            padding: 15px 20px;
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1rem;
        }}
        
        .option:hover {{
            background: #e9ecef;
            transform: translateY(-2px);
        }}
        
        .option.selected {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .option.correct {{
            background: #28a745;
            color: white;
            border-color: #28a745;
        }}
        
        .option.incorrect {{
            background: #dc3545;
            color: white;
            border-color: #dc3545;
        }}
        
        .controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 30px;
        }}
        
        .btn {{
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        
        .btn-primary {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .result {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            margin: 20px 0;
        }}
        
        .result h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        
        .score {{
            font-size: 3rem;
            font-weight: bold;
            color: #28a745;
            margin: 20px 0;
        }}
        
        .hidden {{
            display: none;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .question {{
                font-size: 1.1rem;
            }}
            
            .controls {{
                flex-direction: column;
                gap: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 {project_name}</h1>
            <p>在线刷题系统 - {user_prompt}</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value" id="currentQuestion">1</div>
                <div class="stat-label">当前题目</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="correctCount">0</div>
                <div class="stat-label">答对题数</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="totalQuestions">10</div>
                <div class="stat-label">总题数</div>
            </div>
        </div>
        
        <div class="quiz-container" id="quizContainer">
            <div class="question" id="question"></div>
            <div class="options" id="options"></div>
        </div>
        
        <div class="controls">
            <button class="btn btn-secondary" id="prevBtn" onclick="prevQuestion()">上一题</button>
            <button class="btn btn-primary" id="submitBtn" onclick="submitAnswer()">提交答案</button>
            <button class="btn btn-secondary" id="nextBtn" onclick="nextQuestion()">下一题</button>
        </div>
        
        <div class="result hidden" id="result">
            <h2>🎉 测试完成！</h2>
            <div class="score" id="finalScore"></div>
            <p id="resultMessage"></p>
            <button class="btn btn-primary" onclick="restartQuiz()">重新开始</button>
        </div>
    </div>

    <script>
        const questions = [
            {{
                question: "证券市场的基本功能不包括以下哪项？",
                options: ["融资功能", "价格发现功能", "风险管理功能", "商品生产功能"],
                correct: 3
            }},
            {{
                question: "以下哪个不是证券交易所的职能？",
                options: ["提供交易场所", "制定交易规则", "发行证券", "监管交易"],
                correct: 2
            }},
            {{
                question: "股票的面值通常是多少？",
                options: ["1元", "10元", "100元", "1000元"],
                correct: 0
            }},
            {{
                question: "以下哪种证券属于债权性证券？",
                options: ["普通股", "优先股", "公司债券", "认股权证"],
                correct: 2
            }},
            {{
                question: "证券投资基金的管理费通常按什么收取？",
                options: ["固定金额", "基金资产净值的一定比例", "投资收益的一定比例", "基金份额数量"],
                correct: 1
            }},
            {{
                question: "以下哪个指标用于衡量股票的估值水平？",
                options: ["ROE", "P/E", "EPS", "ROA"],
                correct: 1
            }},
            {{
                question: "证券公司的核心业务不包括？",
                options: ["证券经纪", "证券承销", "资产管理", "房地产开发"],
                correct: 3
            }},
            {{
                question: "以下哪种风险属于系统性风险？",
                options: ["信用风险", "流动性风险", "市场风险", "经营风险"],
                correct: 2
            }},
            {{
                question: "股票分红除权后，股价通常会？",
                options: ["上涨", "下跌", "不变", "无法预测"],
                correct: 1
            }},
            {{
                question: "以下哪个不是证券市场的参与者？",
                options: ["投资者", "融资者", "中介机构", "商品生产商"],
                correct: 3
            }}
        ];
        
        let currentQuestionIndex = 0;
        let selectedAnswer = null;
        let correctAnswers = 0;
        let answers = [];
        
        function loadQuestion() {{
            const question = questions[currentQuestionIndex];
            document.getElementById('question').textContent = question.question;
            
            const optionsContainer = document.getElementById('options');
            optionsContainer.innerHTML = '';
            
            question.options.forEach((option, index) => {{
                const optionElement = document.createElement('div');
                optionElement.className = 'option';
                optionElement.textContent = option;
                optionElement.onclick = () => selectOption(index);
                optionsContainer.appendChild(optionElement);
            }});
            
            updateProgress();
            updateStats();
            updateButtons();
        }}
        
        function selectOption(index) {{
            selectedAnswer = index;
            const options = document.querySelectorAll('.option');
            options.forEach((option, i) => {{
                option.classList.remove('selected');
                if (i === index) {{
                    option.classList.add('selected');
                }}
            }});
        }}
        
        function submitAnswer() {{
            if (selectedAnswer === null) {{
                alert('请选择一个答案');
                return;
            }}
            
            const question = questions[currentQuestionIndex];
            const options = document.querySelectorAll('.option');
            
            options.forEach((option, i) => {{
                option.classList.remove('selected');
                if (i === question.correct) {{
                    option.classList.add('correct');
                }} else if (i === selectedAnswer && i !== question.correct) {{
                    option.classList.add('incorrect');
                }}
            }});
            
            if (selectedAnswer === question.correct) {{
                correctAnswers++;
            }}
            
            answers[currentQuestionIndex] = selectedAnswer;
            
            setTimeout(() => {{
                if (currentQuestionIndex < questions.length - 1) {{
                    nextQuestion();
                }} else {{
                    showResult();
                }}
            }}, 1500);
        }}
        
        function nextQuestion() {{
            if (currentQuestionIndex < questions.length - 1) {{
                currentQuestionIndex++;
                selectedAnswer = null;
                loadQuestion();
            }}
        }}
        
        function prevQuestion() {{
            if (currentQuestionIndex > 0) {{
                currentQuestionIndex--;
                selectedAnswer = answers[currentQuestionIndex] || null;
                loadQuestion();
            }}
        }}
        
        function updateProgress() {{
            const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        }}
        
        function updateStats() {{
            document.getElementById('currentQuestion').textContent = currentQuestionIndex + 1;
            document.getElementById('correctCount').textContent = correctAnswers;
        }}
        
        function updateButtons() {{
            document.getElementById('prevBtn').disabled = currentQuestionIndex === 0;
            document.getElementById('nextBtn').style.display = 
                currentQuestionIndex === questions.length - 1 ? 'none' : 'inline-block';
        }}
        
        function showResult() {{
            document.getElementById('quizContainer').classList.add('hidden');
            document.getElementById('controls').classList.add('hidden');
            document.getElementById('result').classList.remove('hidden');
            
            const percentage = (correctAnswers / questions.length) * 100;
            document.getElementById('finalScore').textContent = percentage.toFixed(1) + '%';
            
            let message = '';
            if (percentage >= 90) {{
                message = '🎉 优秀！您对证券知识掌握得很好！';
            }} else if (percentage >= 70) {{
                message = '👍 良好！继续保持，还有提升空间！';
            }} else if (percentage >= 60) {{
                message = '📚 及格！建议继续学习巩固知识！';
            }} else {{
                message = '💪 需要加强！建议系统学习证券知识！';
            }}
            
            document.getElementById('resultMessage').textContent = message;
        }}
        
        function restartQuiz() {{
            currentQuestionIndex = 0;
            selectedAnswer = null;
            correctAnswers = 0;
            answers = [];
            
            document.getElementById('quizContainer').classList.remove('hidden');
            document.getElementById('controls').classList.remove('hidden');
            document.getElementById('result').classList.add('hidden');
            
            loadQuestion();
        }}
        
        // 初始化
        loadQuestion();
        
        // 键盘支持
        document.addEventListener('keydown', (e) => {{
            if (e.key >= '1' && e.key <= '4') {{
                const index = parseInt(e.key) - 1;
                if (index < questions[currentQuestionIndex].options.length) {{
                    selectOption(index);
                }}
            }} else if (e.key === 'Enter') {{
                submitAnswer();
            }} else if (e.key === 'ArrowRight') {{
                nextQuestion();
            }} else if (e.key === 'ArrowLeft') {{
                prevQuestion();
            }}
        }});
    </script>
</body>
</html>"""

    def generate_calculator_template(self, project_name: str, user_prompt: str) -> str:
        """生成计算器模板"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - 计算器</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 400px;
            width: 100%;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #333;
            font-size: 2rem;
            margin-bottom: 10px;
        }}
        
        .display {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }}
        
        .display-text {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #333;
            word-break: break-all;
        }}
        
        .buttons {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .btn {{
            padding: 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1.5rem;
            font-weight: bold;
            transition: all 0.3s ease;
            background: #f8f9fa;
            color: #333;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .btn-number {{
            background: #e9ecef;
        }}
        
        .btn-operator {{
            background: #667eea;
            color: white;
        }}
        
        .btn-equals {{
            background: #28a745;
            color: white;
        }}
        
        .btn-clear {{
            background: #dc3545;
            color: white;
        }}
        
        .btn-zero {{
            grid-column: span 2;
        }}
        
        .history {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .history h3 {{
            color: #333;
            margin-bottom: 15px;
        }}
        
        .history-item {{
            padding: 8px 12px;
            background: white;
            border-radius: 5px;
            margin: 5px 0;
            font-family: monospace;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .history-empty {{
            text-align: center;
            color: #999;
            font-style: italic;
        }}
        
        @media (max-width: 480px) {{
            .container {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.5rem;
            }}
            
            .display-text {{
                font-size: 2rem;
            }}
            
            .btn {{
                padding: 15px;
                font-size: 1.2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧮 {project_name}</h1>
            <p>科学计算器 - {user_prompt}</p>
        </div>
        
        <div class="display">
            <div class="display-text" id="display">0</div>
        </div>
        
        <div class="buttons">
            <button class="btn btn-clear" onclick="clearAll()">C</button>
            <button class="btn btn-clear" onclick="clearEntry()">CE</button>
            <button class="btn btn-operator" onclick="inputOperator('%')">%</button>
            <button class="btn btn-operator" onclick="inputOperator('/')">÷</button>
            
            <button class="btn btn-number" onclick="inputNumber('7')">7</button>
            <button class="btn btn-number" onclick="inputNumber('8')">8</button>
            <button class="btn btn-number" onclick="inputNumber('9')">9</button>
            <button class="btn btn-operator" onclick="inputOperator('*')">×</button>
            
            <button class="btn btn-number" onclick="inputNumber('4')">4</button>
            <button class="btn btn-number" onclick="inputNumber('5')">5</button>
            <button class="btn btn-number" onclick="inputNumber('6')">6</button>
            <button class="btn btn-operator" onclick="inputOperator('-')">-</button>
            
            <button class="btn btn-number" onclick="inputNumber('1')">1</button>
            <button class="btn btn-number" onclick="inputNumber('2')">2</button>
            <button class="btn btn-number" onclick="inputNumber('3')">3</button>
            <button class="btn btn-operator" onclick="inputOperator('+')">+</button>
            
            <button class="btn btn-number btn-zero" onclick="inputNumber('0')">0</button>
            <button class="btn btn-number" onclick="inputNumber('.')">.</button>
            <button class="btn btn-equals" onclick="calculate()">=</button>
        </div>
        
        <div class="history">
            <h3>计算历史</h3>
            <div id="historyList">
                <div class="history-empty">暂无计算记录</div>
            </div>
        </div>
    </div>

    <script>
        let display = document.getElementById('display');
        let currentInput = '0';
        let operator = null;
        let previousInput = null;
        let waitingForOperand = false;
        let history = [];
        
        function updateDisplay() {{
            display.textContent = currentInput;
        }}
        
        function inputNumber(number) {{
            if (waitingForOperand) {{
                currentInput = number;
                waitingForOperand = false;
            }} else {{
                currentInput = currentInput === '0' ? number : currentInput + number;
            }}
            updateDisplay();
        }}
        
        function inputOperator(nextOperator) {{
            const inputValue = parseFloat(currentInput);
            
            if (previousInput === null) {{
                previousInput = inputValue;
            }} else if (operator) {{
                const currentValue = previousInput || 0;
                const newValue = calculate(currentValue, inputValue, operator);
                
                currentInput = String(newValue);
                previousInput = newValue;
                updateDisplay();
            }}
            
            waitingForOperand = true;
            operator = nextOperator;
        }}
        
        function calculate(firstOperand, secondOperand, operator) {{
            switch (operator) {{
                case '+':
                    return firstOperand + secondOperand;
                case '-':
                    return firstOperand - secondOperand;
                case '*':
                    return firstOperand * secondOperand;
                case '/':
                    return firstOperand / secondOperand;
                case '%':
                    return firstOperand % secondOperand;
                default:
                    return secondOperand;
            }}
        }}
        
        function calculate() {{
            const inputValue = parseFloat(currentInput);
            
            if (previousInput !== null && operator) {{
                const newValue = calculate(previousInput, inputValue, operator);
                
                // 添加到历史记录
                const expression = `${{previousInput}} ${{getOperatorSymbol(operator)}} ${{inputValue}} = ${{newValue}}`;
                addToHistory(expression);
                
                currentInput = String(newValue);
                previousInput = null;
                operator = null;
                waitingForOperand = true;
                updateDisplay();
            }}
        }}
        
        function getOperatorSymbol(op) {{
            switch (op) {{
                case '+': return '+';
                case '-': return '-';
                case '*': return '×';
                case '/': return '÷';
                case '%': return '%';
                default: return op;
            }}
        }}
        
        function clearAll() {{
            currentInput = '0';
            previousInput = null;
            operator = null;
            waitingForOperand = false;
            updateDisplay();
        }}
        
        function clearEntry() {{
            currentInput = '0';
            updateDisplay();
        }}
        
        function addToHistory(expression) {{
            history.unshift(expression);
            if (history.length > 10) {{
                history.pop();
            }}
            updateHistory();
        }}
        
        function updateHistory() {{
            const historyList = document.getElementById('historyList');
            
            if (history.length === 0) {{
                historyList.innerHTML = '<div class="history-empty">暂无计算记录</div>';
                return;
            }}
            
            historyList.innerHTML = '';
            history.forEach(item => {{
                const div = document.createElement('div');
                div.className = 'history-item';
                div.textContent = item;
                historyList.appendChild(div);
            }});
        }}
        
        // 键盘支持
        document.addEventListener('keydown', (e) => {{
            if (e.key >= '0' && e.key <= '9') {{
                inputNumber(e.key);
            }} else if (e.key === '.') {{
                inputNumber('.');
            }} else if (e.key === '+') {{
                inputOperator('+');
            }} else if (e.key === '-') {{
                inputOperator('-');
            }} else if (e.key === '*') {{
                inputOperator('*');
            }} else if (e.key === '/') {{
                e.preventDefault();
                inputOperator('/');
            }} else if (e.key === '%') {{
                inputOperator('%');
            }} else if (e.key === 'Enter' || e.key === '=') {{
                calculate();
            }} else if (e.key === 'Escape') {{
                clearAll();
            }} else if (e.key === 'Backspace') {{
                clearEntry();
            }}
        }});
        
        // 从本地存储加载历史记录
        function loadHistory() {{
            const savedHistory = localStorage.getItem('calculatorHistory');
            if (savedHistory) {{
                history = JSON.parse(savedHistory);
                updateHistory();
            }}
        }}
        
        // 保存历史记录到本地存储
        function saveHistory() {{
            localStorage.setItem('calculatorHistory', JSON.stringify(history));
        }}
        
        // 重写addToHistory以包含保存功能
        const originalAddToHistory = addToHistory;
        addToHistory = function(expression) {{
            originalAddToHistory(expression);
            saveHistory();
        }};
        
        // 初始化
        loadHistory();
    </script>
</body>
</html>"""

    def generate_hello_template(self, project_name: str, user_prompt: str) -> str:
        """生成Hello World模板"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - 欢迎页面</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        
        .container {{
            text-align: center;
            color: white;
            z-index: 2;
            position: relative;
        }}
        
        .title {{
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 20px;
            animation: fadeInUp 1s ease-out;
        }}
        
        .subtitle {{
            font-size: 1.5rem;
            margin-bottom: 30px;
            opacity: 0.9;
            animation: fadeInUp 1s ease-out 0.3s both;
        }}
        
        .keyword {{
            font-size: 2rem;
            background: rgba(255,255,255,0.2);
            padding: 15px 30px;
            border-radius: 50px;
            margin: 30px 0;
            backdrop-filter: blur(10px);
            animation: fadeInUp 1s ease-out 0.6s both;
        }}
        
        .info {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            backdrop-filter: blur(10px);
            animation: fadeInUp 1s ease-out 0.9s both;
        }}
        
        .time {{
            font-size: 1.2rem;
            margin: 20px 0;
            opacity: 0.8;
        }}
        
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }}
        
        .feature {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            animation: fadeInUp 1s ease-out 1.2s both;
        }}
        
        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 15px;
        }}
        
        .feature-title {{
            font-size: 1.3rem;
            margin-bottom: 10px;
        }}
        
        .feature-desc {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        
        .background {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            opacity: 0.1;
        }}
        
        .particle {{
            position: absolute;
            background: white;
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }}
        
        .controls {{
            margin-top: 40px;
            animation: fadeInUp 1s ease-out 1.5s both;
        }}
        
        .btn {{
            padding: 15px 30px;
            margin: 10px;
            background: rgba(255,255,255,0.2);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 30px;
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(50px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes float {{
            0%, 100% {{
                transform: translateY(0) rotate(0deg);
            }}
            50% {{
                transform: translateY(-20px) rotate(180deg);
            }}
        }}
        
        @media (max-width: 768px) {{
            .title {{
                font-size: 2.5rem;
            }}
            
            .subtitle {{
                font-size: 1.2rem;
            }}
            
            .keyword {{
                font-size: 1.5rem;
                padding: 10px 20px;
            }}
            
            .info {{
                padding: 20px;
            }}
            
            .features {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="background" id="background"></div>
    
    <div class="container">
        <div class="title">🎉 {project_name}</div>
        <div class="subtitle">欢迎使用 AI 项目管理系统</div>
        
        <div class="keyword">"{user_prompt}"</div>
        
        <div class="time" id="currentTime"></div>
        
        <div class="info">
            <h3>✨ 系统信息</h3>
            <p>🤖 生成方式: 高质量模板</p>
            <p>⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🎯 项目关键字: {user_prompt}</p>
            <p>🔧 技术栈: HTML5 + CSS3 + JavaScript</p>
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">🚀</div>
                <div class="feature-title">快速生成</div>
                <div class="feature-desc">AI驱动的智能网页生成，快速创建功能完整的应用</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📱</div>
                <div class="feature-title">响应式设计</div>
                <div class="feature-desc">完美适配各种设备，提供一致的用户体验</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🎨</div>
                <div class="feature-title">美观界面</div>
                <div class="feature-desc">现代化的设计风格，流畅的动画效果</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="changeBackground()">🌈 切换背景</button>
            <button class="btn" onclick="toggleAnimation()">⚡ 切换动画</button>
            <button class="btn" onclick="showAbout()">ℹ️ 关于</button>
        </div>
    </div>

    <script>
        let animationEnabled = true;
        let backgroundIndex = 0;
        
        const backgrounds = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
            'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)'
        ];
        
        function updateTime() {{
            const now = new Date();
            const timeString = now.toLocaleString('zh-CN', {{
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }});
            document.getElementById('currentTime').textContent = `🕐 当前时间: ${{timeString}}`;
        }}
        
        function changeBackground() {{
            backgroundIndex = (backgroundIndex + 1) % backgrounds.length;
            document.body.style.background = backgrounds[backgroundIndex];
        }}
        
        function toggleAnimation() {{
            animationEnabled = !animationEnabled;
            const particles = document.querySelectorAll('.particle');
            particles.forEach(particle => {{
                particle.style.animationPlayState = animationEnabled ? 'running' : 'paused';
            }});
        }}
        
        function showAbout() {{
            alert(`🎉 ${{"{project_name}"}}\\n\\n` +
                  `📝 项目描述: ${{"{user_prompt}"}}\\n` +
                  `🤖 生成方式: 高质量模板\\n` +
                  `⏰ 生成时间: ${{"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}}\\n` +
                  `🔧 技术栈: HTML5 + CSS3 + JavaScript\\n\\n` +
                  `✨ 这是一个由AI项目管理系统生成的演示页面`);
        }}
        
        function createParticles() {{
            const background = document.getElementById('background');
            for (let i = 0; i < 50; i++) {{
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.width = particle.style.height = (Math.random() * 4 + 1) + 'px';
                particle.style.animationDelay = Math.random() * 6 + 's';
                particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
                background.appendChild(particle);
            }}
        }}
        
        // 键盘事件
        document.addEventListener('keydown', (e) => {{
            switch (e.key) {{
                case 'b':
                case 'B':
                    changeBackground();
                    break;
                case 'a':
                case 'A':
                    toggleAnimation();
                    break;
                case 'i':
                case 'I':
                    showAbout();
                    break;
                case ' ':
                    e.preventDefault();
                    changeBackground();
                    break;
            }}
        }});
        
        // 初始化
        createParticles();
        updateTime();
        setInterval(updateTime, 1000);
        
        // 欢迎消息
        setTimeout(() => {{
            console.log('🎉 欢迎使用 AI 项目管理系统!');
            console.log('🔗 项目: {project_name}');
            console.log('🎯 关键字: {user_prompt}');
            console.log('⌨️ 快捷键: B-切换背景, A-切换动画, I-关于, 空格-切换背景');
        }}, 1000);
    </script>
</body>
</html>"""

# 全局模板生成器实例
template_generator = TemplateGenerator()
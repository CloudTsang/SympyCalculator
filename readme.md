使用sympy库进行小学算式运算律计算的算法，也就是交换律、结合律、拆分律等等得出步骤。   
最初预定是学习使用强化学习（Reinforcement Learning）计算每一步的得分进行解题。但是一来本人学艺不精难以构建出合适的Env，二来使用sympy进行一些数据处理、验证的时候感觉这个库已经很好用就尝试直接用了。  
当然sympy本身是直接算出最终答案的，在分步这点上写了一些代码。  
运行：

    python sympy_calculator.py

更多运行结果可以查看项目内的docx，由于sympy本身的强大，比起代码怎么写，苦恼更多是“使用简便运算律的‘原因’究竟是什么？”这种问题，只要相加等于10就应该运用结合律吗？实际并不是。把11拆成10和1就一定变得简便了吗？也不是。对哪个数使用什么运算律，大概在强化学习里就是需要进行打分的action，对我来说即使只是小学数学也是理解不足，导致算法最后并没有用到产品中。  

![结果](https://gitee.com/cloudtsang/SympyCalculator/raw/main/test1.png)
![结果](https://gitee.com/cloudtsang/SympyCalculator/raw/main/test2.png)
![结果](https://gitee.com/cloudtsang/SympyCalculator/raw/main/test3.png)
![结果](https://gitee.com/cloudtsang/SympyCalculator/raw/main/test4.png)
![结果](https://gitee.com/cloudtsang/SympyCalculator/raw/main/test5.png)
![结果](https://gitee.com/cloudtsang/SympyCalculator/raw/main/test6.png)


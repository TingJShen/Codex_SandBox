# 近一年个性化 LLM 论文调研综述

调研窗口：2025-05-07 至 2026-05-07。中心背景论文为 LaMP 与 OPPU；它们早于窗口，但作为本综述的两条主线单独列出。
本次采用宽口径：LLM 个性化、用户画像/记忆、个性化对齐、个性化 RAG/检索、个性化 PEFT/LoRA、个性化 agent、LLM 推荐系统、隐私/联邦/on-device 个性化均纳入。
扫描统计：raw_records_total=7199，其中 arXiv=6900，OpenReview paper-like=299；最终近一年收录 280 篇，另列 2 篇中心背景。
排序规则：优先 LaMP/OPPU 继承关系、标题/摘要中的个性化信号、方法相关性、OpenReview/重要会议公开记录、benchmark/数据集贡献和方向覆盖。自动抽取的数据集字段若摘要未写明，会显式标注“需正文核查”。

## 中心背景论文

### 1. [LaMP: When Large Language Models Meet Personalization](https://arxiv.org/abs/2304.11406)

- 发表时间/状态：2023-04-22; ACL 2024；ACL 2024 long paper / benchmark
- 重要性与相关性：center；score=99
- 方法介绍：LaMP 把用户历史作为 profile，引入一组个性化语言模型任务，用统一框架评估检索用户画像、拼接上下文、微调和零样本生成等方法。它把“个性化”从单个推荐任务扩展为可复现的 LLM benchmark。
- 数据集：LaMP-1 到 LaMP-7：个性化引用识别、电影标签、商品评分、新闻标题、学术标题、邮件主题、推文改写等任务。
- 主要结论：主要结论是：用户历史能显著影响 LLM 输出质量，但收益依赖 profile 检索质量、任务类型和训练/推理方式；简单拼接并不总是最优。
- 与 LaMP/OPPU 的关系：这是本综述的中心基准线，后续 profile/RAG、评测和 LongLaMP 类工作大多直接或间接继承它的问题设定。

### 2. [Democratizing Large Language Models via Personalized Parameter-Efficient Fine-tuning](https://arxiv.org/abs/2402.04401)

- 发表时间/状态：2024-02-07; EMNLP 2024；EMNLP 2024 main / personalized PEFT
- 重要性与相关性：center；score=99
- 方法介绍：论文提出 One PEFT Per User (OPPU)：为每个用户维护一个参数高效模块，把用户行为模式和偏好存入少量可插拔参数，而不是只依赖 prompt 或全量微调。
- 数据集：论文主要在 LaMP 系列个性化任务上验证，并围绕不同用户历史规模和任务类型比较 PEFT 个性化收益。
- 主要结论：主要结论是：个性化 PEFT 能比纯提示/检索方法更稳定地吸收用户偏好，但每用户 adapter 带来训练、存储和冷启动成本，成为后续工作要解决的核心瓶颈。
- 与 LaMP/OPPU 的关系：这是本综述的第二条中心线，后续 hypernetwork、共享-私有 adapter、联邦个性化和效率优化工作多在回应 OPPU 的可扩展性问题。


## Benchmark and Evaluation

这个方向回答“个性化 LLM 到底该如何评测”。LaMP 将用户历史转化为检索式 profile，并把 citation、tagging、rating、headline、title、email subject、tweet paraphrase 等任务统一为可比较的个性化生成/分类基准；近一年工作继续扩展到长历史、多轮记忆、更真实的用户行为和更细粒度的偏好差异。最新进展不是单纯提高分数，而是把评测从静态 profile 推向长期、动态、隐私受限和任务迁移环境。

### 1. [PREMIUM: LLM Personalization with Individual-level Preference Feedback](https://openreview.net/forum?id=N1pya6kv3g)

- 发表时间/状态：2024-09-26；Submitted to ICLR 2025 / public_note
- 重要性与相关性：core；score=26
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：With an increasing demand for LLM personalization, various methods have been developed to deliver customized LLM experiences, including in-context learning, retrieval augmentation, and parameter-efficient fine-tuning.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Notably, a variant of PREMIUM, PREMIUM-Embed, can effectively capture user preferences while being deployable with laptop-level resources.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 2. [Democratizing Large Language Models via Personalized Parameter-Efficient Fine-tuning](https://openreview.net/forum?id=5Eh8HnBMv9)

- 发表时间/状态：2024-01-01；EMNLP 2024 / public_note
- 重要性与相关性：core；score=25
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalization in large language models (LLMs) is increasingly important, aiming to align the LLMs’ interactions, content, and recommendations with individual user preferences.
- 数据集：LaMP; OPPU
- 主要结论：主要结论可从摘要中的结果句概括为：Recent advances have highlighted effective prompt design by enriching user queries with non-parametric knowledge through behavior history retrieval and textual profiles.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 3. [Reflective Personalization Optimization: A Post-hoc Rewriting Framework for Black-Box Large Language Models](https://openreview.net/forum?id=vKuQ79FJR4)

- 发表时间/状态：2025-11-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=24
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：The personalization of black-box large language models (LLMs) is a critical yet challenging task.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Comprehensive experiments on the LaMP benchmark demonstrate that RPO, by decoupling content generation from personalization, significantly outperforms state-of-the-art baselines.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 4. [MTA: A Merge-then-Adapt Framework for Personalized Large Language Model](https://openreview.net/forum?id=6l1VCa4evM)

- 发表时间/状态：2025-11-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=23
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalized Large Language Models (PLLMs) aim to align model outputs with individual user preferences, a crucial capability for user-centric applications.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Fine-tuning this module enables effective personalization under few-shot settings.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 5. [HYDRA: Model Factorization Framework for Black-Box LLM Personalization](https://openreview.net/forum?id=CKgNgKmHYp)

- 发表时间/状态：2024-05-15；NeurIPS 2024 poster / public_note
- 重要性与相关性：core；score=23
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalization has emerged as a critical research area in modern intelligent systems, focusing on mining users' behavioral history and adapting to their preferences for delivering tailored experiences.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Despite the remarkable few-shot capabilities exhibited by black-box large language models (LLMs), the inherent opacity of their model parameters presents significant challenges in aligning the generated output with individual expectations.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 6. [LaMP: When Large Language Models Meet Personalization](https://openreview.net/forum?id=LJvGj5JlSd)

- 发表时间/状态：2024-01-01；ACL (1) 2024 / public_note
- 重要性与相关性：core；score=22
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：This paper highlights the importance of personalization in large language models and introduces the LaMP benchmark — a novel benchmark for training and evaluating language models for producing personalized outputs.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on LaMP for zero-shot and fine-tuned language models demonstrate the efficacy of the proposed retrieval augmentation approach and highlight the impact of personalization in various natural language tasks.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 7. [LaMP-Cap: Personalized Figure Caption Generation With Multimodal Figure Profiles](https://openreview.net/forum?id=jofHQ3wXtW)

- 发表时间/状态：2025-06-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=21
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Figure captions are crucial for helping readers understand and remember a figure's key message.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments with four LLMs show that using profile information consistently helps generate captions closer to the original author-written ones.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 8. [LaMP-QA: A Benchmark for Personalized Long-form Question Answering](https://openreview.net/forum?id=cLp6K54IIT)

- 发表时间/状态：2025-06-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=21
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalization is essential for question answering systems that are user-centric.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Our results show that incorporating the personalized context provided leads to up to 39% performance improvements.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 9. [ClusterRAG: Cluster-Based Collaborative Filtering for Personalized Retrieval-Augmented Generation](https://openreview.net/forum?id=ECk4OIkgUE)

- 发表时间/状态：2026-01-05；ACL ARR 2026 January Submission / public_note
- 重要性与相关性：core；score=20
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalized Retrieval-Augmented Generation (RAG) relies on accurately selecting user-relevant documents.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on the LaMP benchmark demonstrate that jointly leveraging the target user’s profile and profiles from top similar users consistently yields the best performance across diverse tasks.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 10. [Large Language Models Empowered Personalized Web Agents](https://openreview.net/forum?id=kAzqfqsCC5)

- 发表时间/状态：2024-09-30；WWW 2025 Oral / public_note
- 重要性与相关性：core；score=20
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Web agents have emerged as a promising direction to automate Web task completion based on user instructions, significantly enhancing user experience.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Web agents have emerged as a promising direction to automate Web task completion based on user instructions, significantly enhancing user experience.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 11. [DeepTutor: Towards Agentic Personalized Tutoring](https://arxiv.org/abs/2604.26962v1)

- 发表时间/状态：2026-04-10；arXiv / preprint
- 重要性与相关性：core；score=19
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Education represents one of the most promising real-world applications for Large Language Models (LLMs).
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments show that DeepTutor improves personalized tutoring quality while maintaining general agentic reasoning abilities.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 12. [When Personalization Legitimizes Risks: Uncovering Safety Vulnerabilities in Personalized Dialogue Agents](https://openreview.net/forum?id=EODV7WBADQ)

- 发表时间/状态：2026-01-06；ACL ARR 2026 January Submission / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Long-term memory enables large language model (LLM) agents to support personalized and sustained interactions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We further provide mechanistic evidence for intent legitimation from internal representation space, and propose a lightweight detection–reflection method that effectively reduces safety degradation.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 13. [Personalized Large Language Model Assistant with Evolving Conditional Memory](https://openreview.net/forum?id=PrJUwnwUM2)

- 发表时间/状态：2025-01-01；COLING 2025 / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：With the rapid development of large language models, AI assistants like ChatGPT have become increasingly integrated into people’s works and lives but are limited in personalized services.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Generally, the assistant generates a set of records from the dialogue, stores them in a memory bank, and retrieves related memory to improve the quality of the response.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 14. [AFA: Identity-Aware Memory for Preventing Persona Confusion in Multi-User Dialogue](https://arxiv.org/abs/2604.25022v1)

- 发表时间/状态：2026-04-27；arXiv / preprint
- 重要性与相关性：core；score=18
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：When multiple people share a single voice assistant, the system conflates their histories: one resident's preferences can leak into another's responses, eroding utility and trust.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We call this failure mode persona confusion, and we show it is a measurable problem in today's single-user dialogue systems when deployed in shared environments.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 15. [Personalized Benchmarking: Evaluating LLMs by Individual Preferences](https://arxiv.org/abs/2604.18943v1)

- 发表时间/状态：2026-04-21；arXiv / preprint
- 重要性与相关性：core；score=18
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：With the rise in capabilities of large language models (LLMs) and their deployment in real-world tasks, evaluating LLM alignment with human preferences has become an important challenge.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We demonstrate that individual rankings of LLM models diverge dramatically from aggregate LLM rankings, with Bradley-Terry correlations averaging only $ρ= 0.04$ (57\% of users show near-zero or negative correlation) and ELO ratings showing moderate correlation ($ρ= 0.43$).
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 16. [Latent Preference Modeling for Cross-Session Personalized Tool Calling](https://arxiv.org/abs/2604.17886v1)

- 发表时间/状态：2026-04-20；arXiv / preprint
- 重要性与相关性：core；score=18
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Users often omit essential details in their requests to LLM-based agents, resulting in under-specified inputs for tool use.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Through a generate--verify--refine loop, it extracts reusable constraints from history and improves tool-calling accuracy while using only 1.24% of the tokens required by full-history prompting.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 17. [Personalized Content Restriction for Large Language Models](https://openreview.net/forum?id=ISudz0Jh17)

- 发表时间/状态：2026-04-02；Under review for TMLR / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large Language Models (LLMs) have achieved remarkable success across diverse applications, yet enforcing user-specific and personalized content restrictions remains challenging due to their vast generation space.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large Language Models (LLMs) have achieved remarkable success across diverse applications, yet enforcing user-specific and personalized content restrictions remains challenging due to their vast generation space.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 18. [MemoryCD: Benchmarking Long-Context User Memory of LLM Agents for Lifelong Cross-Domain Personalization](https://openreview.net/forum?id=Lpq4aEqvmg)

- 发表时间/状态：2026-02-16；LLA 2026 Poster / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Recent advancements in Large Language Models (LLMs) have expanded context windows to million-token scales, yet benchmarks for evaluating memory remain limited to short-session synthetic dialogues.
- 数据集：Amazon
- 主要结论：主要结论可从摘要中的结果句概括为：We construct a multi-faceted long-context memory evaluation pipeline of 14 state-of-the-art LLM base models with 6 memory method baselines on 4 distinct personalization tasks over 12 diverse domains to evaluate an agent's ability to simulate real user behaviors in both single and cross-domain settings.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 19. [Towards Effective Model Editing for LLM Personalization](https://openreview.net/forum?id=2cHXYZRcg2)

- 发表时间/状态：2025-12-29；ACL ARR 2026 January Submission / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalization is becoming indispensable for LLMs to align with individual user preferences and needs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Across experimental settings, Personalization Editing achieves higher editing accuracy and greater computational efficiency than fine-tuning, while outperforming prompting-based baselines in multi-turn conversations and implicit preference questions settings.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 20. [PersonalLLM: Tailoring LLMs to Individual Preferences](https://openreview.net/forum?id=dgK36oHNkS)

- 发表时间/状态：2024-09-10；Pluralistic-Alignment 2024 / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：As LLMs become capable of complex tasks, there is growing potential for personalized interactions tailored to the subtle and idiosyncratic preferences of the user.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We explore basic in-context learning and meta-learning baselines to illustrate the utility of PersonalLLM and highlight the need for future methodological development.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 21. [MemRerank: Preference Memory for Personalized Product Reranking](https://arxiv.org/abs/2603.29247v2)

- 发表时间/状态：2026-03-31；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：LLM-based shopping agents increasingly rely on long purchase histories and multi-turn interactions for personalization, yet naively appending raw history to prompts is often ineffective due to noise, length, and relevance mismatch.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：LLM-based shopping agents increasingly rely on long purchase histories and multi-turn interactions for personalization, yet naively appending raw history to prompts is often ineffective due to noise, length, and relevance mismatch.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 22. [PersonalBench: A Human-Grounded Benchmark for LLM Personalization](https://openreview.net/forum?id=XJ9MTjcRAK)

- 发表时间/状态：2026-03-10；MSLD 2026 Poster / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large language models (LLMs) are increasingly deployed as personal assistants, yet their ability to produce genuinely user-aligned responses remains unclear.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Through this process, we uncover a critical bottleneck: selecting contextually relevant attributes is surprisingly difficult for LLMs, with model selections showing poor agreement with those of real users.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 23. [Profit: Benchmarking Personalization and Robustness Trade-off in Federated Prompt Tuning](https://openreview.net/forum?id=5JsO2DClwk)

- 发表时间/状态：2023-10-02；FL@FM-NeurIPS’23 Oral / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：In many applications of federated learning (FL), clients desire models that are personalized using their local data, yet are also robust in the sense that they retain general global knowledge.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our results show that federated-trained prompts can be surprisingly robust when using a small learning rate with many local epochs for personalization, especially when using an adaptive optimizer as the client optimizer during federated training.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 24. [From Recall to Forgetting: Benchmarking Long-Term Memory for Personalized Agents](https://arxiv.org/abs/2604.20006v1)

- 发表时间/状态：2026-04-21；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalized agents that interact with users over long periods must maintain persistent memory across sessions and update it as circumstances change.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Memory agents offer marginal improvements, exposing shortcomings in long-term memory for personalized agents.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 25. [CoPA: Benchmarking Personalized Question Answering with Data-Informed Cognitive Factors](https://arxiv.org/abs/2604.14773v1)

- 发表时间/状态：2026-04-16；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：While LLMs have demonstrated remarkable potential in Question Answering (QA), evaluating personalization remains a critical bottleneck.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While LLMs have demonstrated remarkable potential in Question Answering (QA), evaluating personalization remains a critical bottleneck.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 26. [Meet Dynamic Individual Preferences: Resolving Conflicting Human Value with Paired Fine-Tuning](https://arxiv.org/abs/2604.12479v1)

- 发表时间/状态：2026-04-14；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Recent advances in large language models (LLMs) have significantly improved the alignment of models with general human preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Recent advances in large language models (LLMs) have significantly improved the alignment of models with general human preferences.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 27. [PeReGrINE: Evaluating Personalized Review Fidelity with User Item Graph Context](https://arxiv.org/abs/2604.07788v1)

- 发表时间/状态：2026-04-09；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：We introduce PeReGrINE, a benchmark and evaluation framework for personalized review generation grounded in graph-structured user--item evidence.
- 数据集：Amazon; Amazon Reviews
- 主要结论：主要结论可从摘要中的结果句概括为：We also study visual evidence as an auxiliary context source and find that it can improve textual quality in some settings, while graph-derived evidence remains the main driver of personalization and consistency.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 28. [Offline Policy Evaluation of Multi-Turn LLM Health Coaching with Real Users](https://openreview.net/forum?id=BE00LfP4Dv)

- 发表时间/状态：2025-09-01；MTI-LLM @ NeurIPS 2025 Poster / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：We study a web-deployed, tool-augmented LLM health coach with real users.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In a pilot with seven users (280 rated turns), offline policy evaluation (OPE) over factorized decision heads (Tool/Style) shows that a uniform heavy-tool policy raises average value on logs but harms specific subgroups, most notably low-health-literacy/high-self-efficacy users.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 29. [PRIME: Large Language Model Personalization with Cognitive Memory and Thought Processes](https://openreview.net/forum?id=lLUtQAINxY)

- 发表时间/状态：2025-07-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large language model (LLM) personalization aims to align model outputs with individuals' unique preferences and opinions.
- 数据集：Reddit
- 主要结论：主要结论可从摘要中的结果句概括为：While recent efforts have implemented various personalization methods, a unified theoretical framework that can systematically understand the drivers of effective personalization is still lacking.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 30. [User Profile with Large Language Models: Construction, Updating, and Benchmarking](https://openreview.net/forum?id=UuSetDynKU)

- 发表时间/状态：2025-02-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：User profile modeling plays a key role in personalized systems, as it requires building accurate profiles and updating them with new information.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We also show a methodology that uses large language models (LLMs) to tackle both profile construction and updating.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 31. [Direct Preference Optimization for LLM-Enhanced Recommendation Systems](https://openreview.net/forum?id=IGsDU2Sl0U)

- 发表时间/状态：2025-01-01；ICME 2025 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large Language Models (LLMs) have exhibited remarkable performance across a wide range of domains, motivating research into their potential for recommendation systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments show that DPO4Rec significantly improves re-ranking performance over strong baselines, demonstrating enhanced instruction-following capabilities of LLMs in recommendation tasks.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 32. [PRIME: Large Language Model Personalization with Cognitive Dual-Memory and Personalized Thought Process](https://openreview.net/forum?id=TIwx9RMHpR)

- 发表时间/状态：2025-01-01；EMNLP 2025 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large language model (LLM) personalization aims to align model outputs with individuals’ unique preferences and opinions.
- 数据集：Reddit
- 主要结论：主要结论可从摘要中的结果句概括为：While recent efforts have implemented various personalization methods, a unified theoretical framework that can systematically understand the drivers of effective personalization is still lacking.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 33. [RMGAP: Benchmarking the Generalization of Reward Models across Diverse Preferences](https://arxiv.org/abs/2605.01831v1)

- 发表时间/状态：2026-05-03；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Reinforcement Learning from Human Feedback has become the standard paradigm for language model alignment, where reward models directly determine alignment effectiveness.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Reinforcement Learning from Human Feedback has become the standard paradigm for language model alignment, where reward models directly determine alignment effectiveness.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 34. [MemEvoBench: Benchmarking Memory MisEvolution in LLM Agents](https://arxiv.org/abs/2604.15774v1)

- 发表时间/状态：2026-04-17；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Equipping Large Language Models (LLMs) with persistent memory enhances interaction continuity and personalization but introduces new safety risks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our analysis suggests that memory evolution is a significant contributor to these failures.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 35. [Self-Evolving LLM Memory Extraction Across Heterogeneous Tasks](https://arxiv.org/abs/2604.11610v1)

- 发表时间/状态：2026-04-13；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：As LLM-based assistants become persistent and personalized, they must extract and retain useful information from past conversations as memory.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on BEHEMOTH show that CluE generalizes effectively across heterogeneous tasks ($+$9.04\% relative gain), consistently outperforming prior self-evolving frameworks.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 36. [Personalized RewardBench: Evaluating Reward Models with Human Aligned Personalization](https://arxiv.org/abs/2604.07343v1)

- 发表时间/状态：2026-04-08；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Pluralistic alignment has emerged as a critical frontier in the development of Large Language Models (LLMs), with reward models (RMs) serving as a central mechanism for capturing diverse human values.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive testing reveals that existing state-of-the-art reward models struggle significantly with personalization, peaking at an accuracy of just 75.94%.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 37. [VehicleMemBench: An Executable Benchmark for Multi-User Long-Term Memory in In-Vehicle Agents](https://arxiv.org/abs/2603.23840v1)

- 发表时间/状态：2026-03-25；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：With the growing demand for intelligent in-vehicle experiences, vehicle-based agents are evolving from simple assistants to long-term companions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments show that powerful models perform well on direct instruction tasks but struggle in scenarios involving memory evolution, particularly when user preferences change dynamically.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 38. [PEARL: Personalized Streaming Video Understanding Model](https://arxiv.org/abs/2603.20422v1)

- 发表时间/状态：2026-03-20；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Human cognition of new concepts is inherently a streaming process: we continuously recognize new objects or identities and update our memories over time.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive evaluations across 8 offline and online models demonstrate that PEARL achieves state-of-the-art performance.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 39. [Personalization Toolkit: Training Free Personalization of Large Vision Language Models](https://openreview.net/forum?id=5mbn3B0O29)

- 发表时间/状态：2025-10-09；Decision pending for TMLR / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personalization of Large Vision-Language Models (LVLMs) involves customizing models to recognize specific users or object instances and to generate contextually tailored responses.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We achieve state-of-the-art results, surpassing existing training-based methods.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 40. [PrefDisco: Evaluating Proactive Personalization through Interactive Preference Discovery](https://openreview.net/forum?id=TpIywUYWWw)

- 发表时间/状态：2025-09-02；MTI-LLM @ NeurIPS 2025 Poster / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Current language models struggle to discover user preferences through conversation, often producing responses that mismatch individual needs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We show that models tend not to ask questions even when provided the option to, even though question asking improves preference alignment.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 41. [A Personalized Conversational Benchmark: Towards Simulating Personalized Conversations](https://openreview.net/forum?id=wC7IjzOANL)

- 发表时间/状态：2025-08-30；MTI-LLM @ NeurIPS 2025 Spotlight / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：We present PersonaConvBench, a large-scale benchmark for evaluating personalized reasoning and generation in multi-turn conversations with large language models (LLMs).
- 数据集：Reddit
- 主要结论：主要结论可从摘要中的结果句概括为：By releasing PersonaConvBench with comprehensive evaluations and codes, we aim to facilitate research on LLMs that can adapt to individuals’ conversational styles, track long-term context, and generate more contextually rich and engaging responses.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 42. [User-Assistant Bias in LLMs](https://openreview.net/forum?id=MVaj7qBFsa)

- 发表时间/状态：2025-08-20；MTI-LLM @ NeurIPS 2025 Poster / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large language models (LLMs) can bias towards relying on their own or the user’s information in chat history, leading to overly stubborn or agreeable behaviors.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Commercial models show various levels of user bias.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 43. [Towards Self-Referential Analytic Assessment: A Profile-Based Approach to L2 Writing Evaluation with LLMs](https://arxiv.org/abs/2605.04298v1)

- 发表时间/状态：2026-05-05；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Automated essay scoring (AES) research often relies on rank-based correlation metrics to validate analytic assessment.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our results show that LLMs tend to outperform single human raters in identifying relative weaknesses (negative feedback) across several proficiency aspects, while human raters remain stronger at identifying relative strengths (positive feedback).
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 44. [MEMAUDIT: An Exact Package-Oracle Evaluation Protocol for Budgeted Long-Term LLM Memory Writing](https://arxiv.org/abs/2605.02199v1)

- 发表时间/状态：2026-05-04；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Long-term LLM agents must compress streams of past interactions into persistent memory before future queries are known.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The resulting artifact provides reusable package generators, certified solvers, natural package exports, external-system scorers, and cached reproducibility metadata for evaluating what memory writers actually preserve under fixed storage budgets.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 45. [NeuroState-Bench: A Human-Calibrated Benchmark for Commitment Integrity in LLM Agent Profiles](https://arxiv.org/abs/2605.01847v2)

- 发表时间/状态：2026-05-03；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Outcome-only evaluation under-specifies whether an evaluated agent profile preserves the commitments required to solve a multi-turn task coherently.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Probe accuracy and state drift achieve slightly higher ROC-AUC, 0.8587, and better Brier/ECE, while HCCIS-CORE has substantially higher point-estimate PR-AUC and remains more closely tied to the benchmark's intended construct.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 46. [ComPASS: Towards Personalized Agentic Social Support via Tool-Augmented Companionship](https://arxiv.org/abs/2604.18356v1)

- 发表时间/状态：2026-04-20；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Developing compassionate interactive systems requires agents to not only understand user emotions but also provide diverse, substantive support.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Comprehensive evaluations across two settings reveal that while the evaluated LLMs can generate valid tool-calling requests with high success rates, significant gaps remain in final response quality.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 47. [Stories of Your Life as Others: A Round-Trip Evaluation of LLM-Generated Life Stories Conditioned on Rich Psychometric Profiles](https://arxiv.org/abs/2604.06071v1)

- 发表时间/状态：2026-04-07；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Personality traits are richly encoded in natural language, and large language models (LLMs) trained on human text can simulate personality when conditioned on persona descriptions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We show that personality scores can be recovered from the generated narratives at levels approaching human test-retest reliability (mean r = 0.750, 85% of the human ceiling), and that recovery is robust across 10 LLM narrative generators and 3 LLM personality scorers spanning 6 providers.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 48. [GISTBench: Evaluating LLM User Understanding via Evidence-Based Interest Verification](https://arxiv.org/abs/2603.29112v1)

- 发表时间/状态：2026-03-31；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：We introduce GISTBench, a benchmark for evaluating Large Language Models' (LLMs) ability to understand users from their interaction histories in recommendation systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our findings reveal performance bottlenecks in current LLMs, particularly their limited ability to accurately count and attribute engagement signals across heterogeneous interaction types.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 49. [MemGround: Long-Term Memory Evaluation Kit for Large Language Models in Gamified Scenarios](https://arxiv.org/abs/2604.14158v1)

- 发表时间/状态：2026-03-23；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Current evaluations of long-term memory in LLMs are fundamentally static.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments reveal that state-of-the-art LLMs and memory agents still struggle with sustained dynamic tracking, temporal event association, and complex reasoning derived from long-term accumulated evidence in interactive environments.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 50. [LAMP: Language-Assisted Motion Planning for Controllable Video Generation](https://openreview.net/forum?id=cVcSrLdtFJ)

- 发表时间/状态：2025-12-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Video generation has achieved remarkable progress in visual fidelity and controllability, enabling conditioning on text, layout, or motion.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Video generation has achieved remarkable progress in visual fidelity and controllability, enabling conditioning on text, layout, or motion.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 51. [A-LAMP: Agentic LLM-Based Framework for Automated MDP Modeling and Policy Generation](https://openreview.net/forum?id=oQdo7H38dC)

- 发表时间/状态：2025-09-01；MTI-LLM @ NeurIPS 2025 Poster / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Applying reinforcement learning (RL) to real-world tasks requires converting informal descriptions into a formal Markov decision process (MDP), implementing an executable environment, and training a policy agent.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Across both classic control and custom RL domains, A-LAMP consistently achieves higher policy generation capability than a single state-of-the-art LLM model.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 52. [ReLay: Personalized LLM-Generated Plain-Language Summaries for Better Understanding, but at What Cost?](https://arxiv.org/abs/2605.00468v1)

- 发表时间/状态：2026-05-01；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Plain Language Summaries (PLS) aim to make research accessible to lay readers, but they are typically written in a one-size-fits-all style that ignores differences in readers' information needs and comprehension.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large language models (LLMs) offer new opportunities for personalizing PLS, but it remains unclear whether personalization helps, which strategies are most effective, and how to balance personalization with safety.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 53. [LUCid: Redefining Relevance For Lifelong Personalization](https://arxiv.org/abs/2604.26996v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Current approaches to lifelong personalization operationalize relevance through semantic proximity, causing them to miss essential user information from topically unrelated interactions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Across multiple architectures, our experiments show significant performance collapse when relevant context must be surfaced from semantically distant history: retrieval recall drops to near zero on the hardest instances, and response alignment remains near 50% even for state-of-the-art models such as Gemini-3-Flash, GPT-5.4, and Claude Haiku.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 54. [EngramaBench: Evaluating Long-Term Conversational Memory with Structured Graph Retrieval](https://arxiv.org/abs/2604.21229v1)

- 发表时间/状态：2026-04-23；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large language model assistants are increasingly expected to retain and reason over information accumulated across many sessions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：GPT-4o full-context achieves the highest composite score (0.6186), while Engrama scores 0.5367 globally but is the only system to score higher than full-context prompting on cross-space reasoning (0.6532 vs.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 55. [HorizonBench: Long-Horizon Personalization with Evolving Preferences](https://arxiv.org/abs/2604.17283v1)

- 发表时间/状态：2026-04-19；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：User preferences evolve across months of interaction, and tracking them requires inferring when a stated preference has been changed by a subsequent life event.
- 数据集：MIND
- 主要结论：主要结论可从摘要中的结果句概括为：This belief-update failure persists across context lengths and expression explicitness levels, identifying state-tracking capability as the primary bottleneck for long-horizon personalization.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 56. [PersonalHomeBench: Evaluating Agents in Personalized Smart Homes](https://arxiv.org/abs/2604.16813v2)

- 发表时间/状态：2026-04-18；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Agentic AI systems are rapidly advancing toward real-world applications, yet their readiness in complex and personalized environments remains insufficiently characterized.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Thorough experimentation reveals a systematic performance reduction as task complexity increases, with pronounced failures in counterfactual reasoning and under partial observability, where effective tool-based information gathering is required.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 57. [Beyond Social Pressure: Benchmarking Epistemic Attack in Large Language Models](https://arxiv.org/abs/2604.07749v1)

- 发表时间/状态：2026-04-09；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large language models (LLMs) can shift their answers under pressure in ways that reflect accommodation rather than reasoning.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Mitigation results are strongly type- and model-dependent: prompt-level anchoring and persona-stability prompts perform best in API settings, while Leading Query Contrastive Decoding is the most reliable intervention for open models.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 58. [Tool Retrieval Bridge: Aligning Vague Instructions with Retriever Preferences via Bridge Model](https://arxiv.org/abs/2604.07816v1)

- 发表时间/状态：2026-04-09；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Tool learning has emerged as a promising paradigm for large language models (LLMs) to address real-world challenges.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To this end, we propose a simple-yet-effective Tool Retrieval Bridge (TRB) approach to boost the performance of tool retrieval for vague instructions.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 59. [BeliefShift: Benchmarking Temporal Belief Consistency and Opinion Drift in LLM Agents](https://arxiv.org/abs/2603.23848v1)

- 发表时间/状态：2026-03-25；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：LLMs are increasingly used as long-running conversational agents, yet every major benchmark evaluating their memory treats user information as static facts to be stored and retrieved.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We further introduce four novel evaluation metrics: Belief Revision Accuracy (BRA), Drift Coherence Score (DCS), Contradiction Resolution Rate (CRR), and Evidence Sensitivity Index (ESI).
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 60. [LAMP: Implicit Language Map for Robot Navigation](https://openreview.net/forum?id=ayqQKmCtX1)

- 发表时间/状态：2026-03-08；IEEE Robotics and Automation Letters / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Recent advances in vision-language models have made zero-shot navigation feasible, enabling robots to interpret and follow natural language instructions without requiring labeling.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：This refinement is particularly effective at selecting goal regions not directly observed by leveraging semantic similarities in the learned feature space.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 61. [Conf-Profile: A Confidence-Driven Reasoning Paradigm for Label-Free User Profiling](https://openreview.net/forum?id=lIjoiq3tYH)

- 发表时间/状态：2025-09-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：User profiling, as a core technique for user understanding, aims to infer structural attributes from user information.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We first synthesize high-quality labels by leveraging advanced LLMs with confidence hints, followed by confidence-weighted voting for accuracy improvement and confidence calibration for a balanced distribution.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 62. [LAMP: A Language Model on the Map](https://openreview.net/forum?id=SVTSiESaI4)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Large Language Models (LLMs) are poised to play an increasingly important role in our lives, providing assistance across a wide array of tasks.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：In the geospatial domain, LLMs have demonstrated the ability to answer generic questions, such as identifying a country's capital; nonetheless, their utility is hindered when it comes to answering fine-grained questions about specific places, such as grocery stores or restaurants, which constitute essential aspects of people's everyday lives.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 63. [LAMP: Extracting Text from Gradients with Language Model Priors](https://openreview.net/forum?id=vCLQEVuBZm)

- 发表时间/状态：2022-01-01；NeurIPS 2022 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Recent work shows that sensitive user data can be reconstructed from gradient updates, breaking the key privacy promise of federated learning.
- 数据集：LaMP
- 主要结论：主要结论可从摘要中的结果句概括为：Recent work shows that sensitive user data can be reconstructed from gradient updates, breaking the key privacy promise of federated learning.
- 与 LaMP/OPPU 的关系：直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。

### 64. [Theory-Grounded Evaluation Exposes the Authorship Gap in LLM Personalization](https://arxiv.org/abs/2604.26460v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Stylistic personalization - making LLMs write in a specific individual's style, rather than merely adapting to task preferences - lacks evaluation grounded in authorship science.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We show that grounding evaluation in authorship verification theory transforms what benchmarks can measure.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。

### 65. [Aggregate vs. Personalized Judges in Business Idea Evaluation: Evidence from Expert Disagreement](https://arxiv.org/abs/2604.22517v1)

- 发表时间/状态：2026-04-24；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。 摘要中的问题陈述是：Evaluating LLM-generated business ideas is often harder to scale than generating them.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Analyses show substantial expert disagreement on fine-grained ordinal scores, while agreement is higher under coarse selection, suggesting structured heterogeneity rather than random noise.
- 与 LaMP/OPPU 的关系：问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。


## Profile Prompting and Personalized RAG

这个方向继承 LaMP 的检索式个性化思路：不改变模型参数，而是在推理时检索用户历史、画像、偏好证据或相似用户样本。发展脉络从简单拼接 profile，走向学习检索器、压缩长期历史、区分稳定偏好和临时意图，以及把 RAG 与记忆模块结合。最新工作更重视上下文预算、噪声 profile、冲突偏好和跨任务泛化。

### 66. [Preference Heads in Large Language Models: A Mechanistic Framework for Interpretable Personalization](https://openreview.net/forum?id=Ly64krMW39)

- 发表时间/状态：2026-05-05；ACL 2026 MainConference / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Large Language Models (LLMs) exhibit strong implicit personalization ability, yet most existing approaches treat this behavior as a black box, relying on prompt engineering or fine tuning on user data.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on widely used personalization benchmarks across multiple LLMs demonstrate consistent gains in personalization fidelity while preserving content coherence and low computational overhead.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 67. [Investigating LLM Variability in Personalized Conversational Information Retrieval](https://openreview.net/forum?id=CPiPD5NYtn)

- 发表时间/状态：2025-10-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Personalized Conversational Information Retrieval (CIR) has seen rapid progress in recent years, driven by the development of Large Language Models (LLMs).
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our results show that human-selected PTKBs consistently enhance retrieval performance, while LLM-based selection methods do not reliably outperform manual choices.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 68. [UniMS-RAG: A Unified Multi-source Retrieval-Augmented Generation for Personalized Dialogue Systems](https://openreview.net/forum?id=7pUeDF1gif)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Large Language Models (LLMs) has shown exceptional capabilities in many natual language understanding and generation tasks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large Language Models (LLMs) has shown exceptional capabilities in many natual language understanding and generation tasks.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 69. [Enhancing Zero-shot Personalized Image Aesthetics Assessment with Profile-aware Multimodal LLM](https://arxiv.org/abs/2604.17233v1)

- 发表时间/状态：2026-04-19；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Personalized image aesthetics assessment (PIAA) aims to predict an individual user's subjective rating of an image, which requires modeling user-specific aesthetic preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on recent PIAA benchmarks show that P-MLLM achieves competitive zero-shot performance and remains effective even with coarse profile information, highlighting the potential of profile-based personalization for zero-shot PIAA.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 70. [RPM: Reasoning-Level Personalization for Black-Box Large Language Models](https://openreview.net/forum?id=oKKVLHFzZ8)

- 发表时间/状态：2025-09-19；ICLR 2026 Poster / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：While black-box large language models are widely deployed, they produce generic outputs that overlook individual user preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments across four diverse tasks demonstrate that RPM consistently outperforms existing response-level methods while simultaneously enhancing both personalization performance and interpretability, providing a promising direction for black-box LLM personalization.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 71. [Understanding the Role of User Profile in the Personalization of Large Language Models](https://openreview.net/forum?id=497r4w3H0C)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Utilizing user profiles to personalize Large Language Models (LLMs) has been shown to enhance the performance on a wide range of tasks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Utilizing user profiles to personalize Large Language Models (LLMs) has been shown to enhance the performance on a wide range of tasks.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 72. [Curiosity and Metacognition: Towards a Unified Framework for Learning and Education in the Age of AI](https://arxiv.org/abs/2604.25648v1)

- 发表时间/状态：2026-04-28；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：This chapter examines the relationship between curiosity and metacognition as critical drivers of autonomous and self-regulated learning.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While promising, our review indicates that these interventions yield mixed results, often proving differentially effective for struggling learners, thereby underscoring the necessity for approaches tailored to individual profiles.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 73. [PersonaPlugin: A Multi-Source Persona Framework for LLM Personalization in Telecommunications](https://openreview.net/forum?id=VnHO50n1xa)

- 发表时间/状态：2026-02-05；Agentic AI in the Wild: From Hallucinations to Reliable Autonomy Poster / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Personalizing large language model (LLM) responses in enterprise environments faces unique challenges: heterogeneous data sources, strict on-premise constraints, and unreliable LLM outputs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our LLM-as-a-Judge evaluation, validated against human judgments ($\kappa=0.71$), demonstrates that persona integration significantly improves personalization: +24.0% in P-Score and +26.7% in Adherence over baseline.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 74. [Beyond One-Size-Fits-All Exercises: Personalizing Computer Science Worksheets with Large Language Models](https://arxiv.org/abs/2604.27433v1)

- 发表时间/状态：2026-04-30；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Large Language Models (LLMs) have been widely applied to student-facing educational tools, this work explores their use in supporting instructors by presenting a practical adaptation of the Framework for Adaptive Content using Educational Technology (FACET) system to generate personalized instructional materials for an Introduction to Computer Programming (CS1) course.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While high-performing students experienced ceiling effects, Low Knowledge/Low Motivation students achieved significantly higher correctness (+18.2%) with personalized support.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 75. [Auditing Preferences for Brands and Cultures in LLMs](https://arxiv.org/abs/2603.18300v1)

- 发表时间/状态：2026-03-18；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Large language models (LLMs) based AI systems increasingly mediate what billions of people see, choose and buy.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Applied to Gemini, GPT, and DeepSeek across 10 topics spanning commerce and culture and more than 2,000 questions, ChoiceEval reveals consistent preferences: U.S.-developed models Gemini and GPT show marked favouritism toward American entities, while China-developed DeepSeek exhibits more balanced yet still detectable geographic preferences.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 76. [Large Language Model Augmented Exercise Retrieval for Personalized Language Learning](https://openreview.net/forum?id=ZFe35Yakur)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：We study the problem of zero-shot exercise retrieval in the context of online language learning, to give learners the ability to explicitly request personalized exercises via natural language.
- 数据集：MS MARCO
- 主要结论：主要结论可从摘要中的结果句概括为：This semantic gap between queries and content dramatically reduces the effectiveness of general-purpose retrieval models pretrained on large scale information retrieval datasets like MS MARCO.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 77. [Time-Sensitive User Profile for Optimizing Search Personlization](https://openreview.net/forum?id=0NZ1jz09ug)

- 发表时间/状态：2014-01-01；UMAP 2014 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Thanks to social Web services, Web search engines have the opportunity to afford personalized search results that better fit the user’s information needs and interests.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To achieve this goal, many personalized search approaches explore user’s social Web interactions to extract his preferences and interests, and use them to model his profile.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。

### 78. [Personalized Cross-Modal Emotional Correlation Learning for Speech-Preserving Facial Expression Manipulation](https://arxiv.org/abs/2604.25255v1)

- 发表时间/状态：2026-04-28；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。 摘要中的问题陈述是：Speech-preserving facial expression manipulation (SPFEM) aims to enhance human expressiveness without altering mouth movements tied to the original speech.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To this end, we propose a Personalized Cross-Modal Emotional Correlation Learning (PCMECL) algorithm that refines VLM-based supervision through two major improvements.
- 与 LaMP/OPPU 的关系：方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。


## Personalized PEFT and Adaptation

这个方向以 OPPU 为中心：为每个用户或用户簇训练少量参数，让偏好沉淀在 adapter/LoRA/hypernetwork 中。它比 prompt 个性化更能吸收隐含行为模式，但面临用户规模、冷启动和更新成本问题。近一年论文重点在共享-私有参数分解、即时 adapter 生成、少样本用户数据、跨用户迁移和可扩展部署。

### 79. [Personalized Pieces: Efficient Personalized Large Language Models through Collaborative Efforts](https://openreview.net/forum?id=KOhM6EosCT)

- 发表时间/状态：2024-01-01；EMNLP 2024 / public_note
- 重要性与相关性：core；score=24
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Personalized large language models (LLMs) aim to tailor interactions, content, and recommendations to individual user preferences.
- 数据集：OPPU
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results show Per-Pcs outperforms non-personalized and PEFT retrieval baselines, offering performance comparable to OPPU with significantly lower resource use across six tasks.
- 与 LaMP/OPPU 的关系：直接延续 OPPU 的每用户 PEFT/adapter 个性化设定，关注可扩展性、效率或少样本用户数据问题。

### 80. [Instant Personalized Large Language Model Adaptation via Hypernetwork](https://openreview.net/forum?id=Fpvk9FDQC2)

- 发表时间/状态：2025-10-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=23
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Personalized large language models (LLMs) tailor content to individual preferences using user profiles or histories.
- 数据集：OPPU
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results demonstrate that our method outperforms both prompt-based personalization and OPPU while using substantially fewer computational resources at deployment.
- 与 LaMP/OPPU 的关系：直接延续 OPPU 的每用户 PEFT/adapter 个性化设定，关注可扩展性、效率或少样本用户数据问题。

### 81. [A Survey of Personalized Large Language Models: Progress and Future Directions](https://openreview.net/forum?id=j0B8ZZfJip)

- 发表时间/状态：2025-02-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=22
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large Language Models (LLMs) excel in handling general knowledge tasks, yet they struggle with user-specific personalization, such as understanding individual emotions, writing styles, and preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This is a highly valuable research topic, as PLLMs can significantly enhance user satisfaction and have broad applications in conversational agents, recommendation systems, emotion recognition, medical assistants, and more.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 82. [User Preference Modeling for Conversational LLM Agents: Weak Rewards from Retrieval-Augmented Interaction](https://arxiv.org/abs/2603.20939v1)

- 发表时间/状态：2026-03-21；arXiv / preprint
- 重要性与相关性：core；score=19
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large language models are increasingly used as personal assistants, yet most lack a persistent user model, forcing users to repeatedly restate preferences across sessions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Under frozen backbones, the main benefit of user-aware retrieval is improved interaction efficiency rather than large gains in raw task accuracy: our full VARS agent achieves the strongest overall performance, matches a strong Reflection baseline in task success, and reduces timeout rate and user effort.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 83. [T-POP: Test-Time Personalization with Online Preference Feedback](https://openreview.net/forum?id=KkT3f2N4oF)

- 发表时间/状态：2025-09-19；Submitted to ICLR 2026 / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Personalizing large language models (LLMs) to individual user preferences is a critical step beyond generating generically helpful responses.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, current personalization methods are ill-suited for new users, as they typically require either slow, resource-intensive fine-tuning or a substantial amount of pre-existing user data, creating a significant cold-start problem.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 84. [PERSA: Reinforcement Learning for Professor-Style Personalized Feedback with LLMs](https://arxiv.org/abs/2605.01123v1)

- 发表时间/状态：2026-05-01；arXiv / preprint
- 重要性与相关性：core；score=18
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large language models (LLMs) can provide automated feedback in educational settings, but aligning an LLMs style with a specific instructors tone while maintaining diagnostic correctness remains challenging.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Overall, PERSA offers a practical route to personalized educational feedback by aligning both what it says (content correctness) and, crucially, how it says it (instructor-like tone and structure).
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 85. [Personalized Visual Representation Alignment for Generative Multimodal Recommendation](https://openreview.net/forum?id=wOaXd83Yio)

- 发表时间/状态：2025-09-19；Submitted to ICLR 2026 / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：With the development of Vision-Language Models (VLMs) for multimodal understanding, recommender systems have increasingly leveraged them to process heterogeneous sources of user-interacted items for recommendation.
- 数据集：Amazon
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on real-world Amazon and H\&M Fashion datasets demonstrate that PerVRA consistently outperforms strong VLM-based methods over diverse personalized tasks.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 86. [AdaptFuse: Training-Free Sequential Preference Learning via Externalized Bayesian Inference](https://arxiv.org/abs/2604.03925v1)

- 发表时间/状态：2026-04-05；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large language models struggle to accumulate evidence across multiple rounds of user interaction, failing to update their beliefs in a manner consistent with Bayesian inference.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：AdaptFuse consistently outperforms both prompting baselines and fine-tuned Bayesian Teaching models on all tasks, with accuracy improving monotonically over interaction rounds.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 87. [User Simulator-Guided Multi-Turn Preference Optimization for Reasoning LLM-based Conversational Recommendation](https://arxiv.org/abs/2604.03671v1)

- 发表时间/状态：2026-04-04；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Conversational Recommender Systems (CRSs) leverage natural language interactions for personalized recommendation, yet information-scarce dialogue histories and single-turn recommendation paradigms may severely hinder accurate modeling of complex user preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Inspired by the multi-step reasoning capabilities of LLMs and the effectiveness of reinforcement learning in policy optimization, we propose SMTPO, a user simulator-guided multi-turn preference optimization conversational recommendation framework.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 88. [On Orchestrating Personalized LLMs](https://openreview.net/forum?id=nKVYQOgD0q)

- 发表时间/状态：2024-09-26；Submitted to ICLR 2025 / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：This paper presents a novel approach to aligning large language models (LLMs) with individual human preferences, sometimes referred to as Reinforcement Learning from *Personalized* Human Feedback (RLPHF).
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Empirical tests show that our method matches or surpasses existing preference merging techniques, providing a scalable, efficient alternative to fine-tuning LLMs for individual personalization.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 89. [Personalized LLM Response Generation with Parameterized Memory Injection](https://openreview.net/forum?id=ZvPPb17INz)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large Language Models (LLMs) have exhibited remarkable proficiency in comprehending and generating natural language.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In this study, we propose a novel \textbf{M}emory-\textbf{i}njected approach using parameter-efficient fine-tuning (PEFT) and along with a Bayesian Optimisation searching strategy to achieve \textbf{L}LM \textbf{P}ersonalization(\textbf{MiLP}).
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 90. [KARMA: Knowledge-Action Regularized Multimodal Alignment for Personalized Search at Taobao](https://arxiv.org/abs/2603.22779v2)

- 发表时间/状态：2026-03-24；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large Language Models (LLMs) are equipped with profound semantic knowledge, making them a natural choice for injecting semantic generalization into personalized search systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This degradation severely cripples the LLM's generalization, failing to bring improvements to personalized search systems.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 91. [Leveraging LLM Reasoning Enhances Personalized Recommender Systems](https://openreview.net/forum?id=rfgx7rSuBF)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Recent advancements have showcased the potential of Large Language Models (LLMs) in executing reasoning tasks, particularly facilitated by Chain-of-Thought (CoT) prompting.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Recent advancements have showcased the potential of Large Language Models (LLMs) in executing reasoning tasks, particularly facilitated by Chain-of-Thought (CoT) prompting.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 92. [MIMIR: A Streamlined Platform for Personalized Agent Tuning in Domain Expertise](https://openreview.net/forum?id=zn9xnuMPUq)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Recently, large language models (LLMs) have evolved into interactive agents, proficient in planning, tool use, and task execution across a wide variety of tasks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：\textsc{Mimir} integrates these features into a cohesive end-to-end platform, facilitating everything from the uploading of personalized files to one-click agent fine-tuning.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 93. [Separable Expert Architecture: Toward Privacy-Preserving LLM Personalization via Composable Adapters and Deletable User Proxies](https://arxiv.org/abs/2604.21571v1)

- 发表时间/状态：2026-04-23；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Current model training approaches incorporate user information directly into shared weights, making individual data removal computationally infeasible without retraining.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The approach converts machine unlearning from an intractable weight-editing problem into a deterministic deletion operation that preserves personalization alongside privacy-enhancing guarantees and is compatible with differentially private stochastic gradient descent (DP-SGD) for privacy-preserving shared model improvement.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 94. [ReRec: Reasoning-Augmented LLM-based Recommendation Assistant via Reinforcement Fine-tuning](https://arxiv.org/abs/2604.07851v1)

- 发表时间/状态：2026-04-09；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：With the rise of LLMs, there is an increasing need for intelligent recommendation assistants that can handle complex queries and provide personalized, reasoning-driven recommendations.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：LLM-based recommenders show potential but face challenges in multi-step reasoning, underscoring the need for reasoning-augmented systems.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 95. [FedPDPO: Federated Personalized Direct Preference Optimization for Large Language Model Alignment](https://arxiv.org/abs/2603.19741v1)

- 发表时间/状态：2026-03-20；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Aligning large language models (LLMs) with human preferences in federated learning (FL) is challenging due to decentralized, privacy-sensitive, and highly non-IID preference data.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on multiple preference datasets demonstrate state-of-the-art performance, achieving up to 4.80% average accuracy improvements in federated intra-domain and cross-domain settings.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 96. [ColorAgent: Building A Robust, Personalized, and Interactive OS Agent](https://openreview.net/forum?id=2CMZpexFKZ)

- 发表时间/状态：2025-10-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：With the advancements in hardware, software, and large language model technologies, the interaction between humans and operating systems has evolved from the command-line interface to the rapidly emerging AI agent interactions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Nonetheless, we note that current benchmarks are insufficient for a comprehensive evaluation of OS agents and propose further exploring directions in future work, particularly in the areas of evaluation paradigms, agent collaboration, and security.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 97. [Customer-R1: personalized simulation of Human Behaviors via RL-based LLM Agent in Online Shopping](https://openreview.net/forum?id=1zNmEA6UqC)

- 发表时间/状态：2025-09-02；MTI-LLM @ NeurIPS 2025 Poster / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Simulating step-wise human behavior with Large Language Models (LLMs) has become an emerging research direction in various domain.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While prior methods, including prompting, supervised fine-tuning (SFT), and reinforcement learning (RL), have shown promise in modeling step-wise behavior, they primarily learn a population-level policy without conditioning on a user’s persona, yielding generic rather than personalized simulations.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 98. [User-Specific Dialogue Generation with User Profile-Aware Pre-Training Model and Parameter-Efficient Fine-Tuning](https://openreview.net/forum?id=nckAOysnWv)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：This paper addresses user-specific dialogs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments reproducing real users' utterances revealed that the proposed model can generate utterances with higher reproducibility than the compared methods, even with a small model.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 99. [Multi-User Dueling Bandits: A Fair Approach using Nash Social Welfare](https://arxiv.org/abs/2605.01961v1)

- 发表时间/状态：2026-05-03；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Learning from human preference data is becoming a useful tool, from fine-tuning large language models to training reinforcement learning agents.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We further derive their regret upper bounds that match the lower-bound dependence on $T$ up to logarithmic factors.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 100. [Pre-trained LLMs Meet Sequential Recommenders: Efficient User-Centric Knowledge Distillation](https://arxiv.org/abs/2604.21536v1)

- 发表时间/状态：2026-04-23；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Sequential recommender systems have achieved significant success in modeling temporal user behavior but remain limited in capturing rich user semantics beyond interaction patterns.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Sequential recommender systems have achieved significant success in modeling temporal user behavior but remain limited in capturing rich user semantics beyond interaction patterns.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 101. [DUET: Joint Exploration of User Item Profiles in Recommendation System](https://arxiv.org/abs/2604.13801v1)

- 发表时间/状态：2026-04-15；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Traditional recommendation systems represent users and items as dense vectors and learn to align them in a shared latent space for relevance estimation.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This paper studies how to construct effective textual profiles for users and items, and how to align them for recommendation.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 102. [What Do Vision-Language Models Encode for Personalized Image Aesthetics Assessment?](https://arxiv.org/abs/2604.11374v1)

- 发表时间/状态：2026-04-13；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Personalized image aesthetics assessment (PIAA) is an important research problem with practical real-world applications.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While methods based on vision-language models (VLMs) are promising candidates for PIAA, it remains unclear whether they internally encode rich, multi-level aesthetic attributes required for effective personalization.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 103. [Personalized Federated Sequential Recommender](https://arxiv.org/abs/2603.22349v1)

- 发表时间/状态：2026-03-22；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：In the domain of consumer electronics, personalized sequential recommendation has emerged as a central task.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Current methodologies in this field are largely centered on modeling user behavior and have achieved notable performance.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 104. [Dual personalization on federated recommendation](https://openreview.net/forum?id=6VpWuvboVD)

- 发表时间/状态：2024-07-12；OpenReview.net/Archive / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Federated recommendation is a new Internet service architecture that aims to provide privacypreserving recommendation services in federated settings.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Moreover, we propose a new dual personalization mechanism to effectively learn fine-grained personalization on both users and items.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 105. [Personalized Large Language Models](https://openreview.net/forum?id=s5fvqmJVaU)

- 发表时间/状态：2024-01-01；ICDM (Workshops) 2024 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large language models (LLMs) have significantly advanced Natural Language Processing (NLP) tasks in recent years.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large language models (LLMs) have significantly advanced Natural Language Processing (NLP) tasks in recent years.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 106. [Uncertainty-Aware Exploratory Direct Preference Optimization for Multimodal Large Language Models](https://arxiv.org/abs/2605.04874v1)

- 发表时间/状态：2026-05-06；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Direct Preference Optimization (DPO) has proven to be an effective solution for mitigating hallucination in Multimodal Large Language Models (MLLMs) by learning from preference pairs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Direct Preference Optimization (DPO) has proven to be an effective solution for mitigating hallucination in Multimodal Large Language Models (MLLMs) by learning from preference pairs.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 107. [Fine-Tuning Impairs the Balancedness of Foundation Models in Long-tailed Personalized Federated Learning](https://arxiv.org/abs/2605.02247v1)

- 发表时间/状态：2026-05-04；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Personalized federated learning (PFL) with foundation models has emerged as a promising paradigm enabling clients to adapt to heterogeneous data distributions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments demonstrate that FedPuReL consistently outperforms state-of-the-art methods, achieving superior performance on both global and personalized models across diverse long-tailed scenarios.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 108. [When RAG Chatbots Expose Their Backend: An Anonymized Case Study of Privacy and Security Risks in Patient-Facing Medical AI](https://arxiv.org/abs/2605.00796v1)

- 发表时间/状态：2026-05-01；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Background: Patient-facing medical chatbots based on retrieval-augmented generation (RAG) are increasingly promoted to deliver accessible, grounded health information.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Commercial LLMs accelerated this assessment, including under a false developer persona; assistance available to auditors is equally available to adversaries.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 109. [How Personal Characteristics Shape User Exploration of Diverse Movie Recommendations with a LLM-Based Multi-Agent System](https://arxiv.org/abs/2604.24405v2)

- 发表时间/状态：2026-04-27；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Diversity is an important evaluation criterion for recommender systems beyond accuracy, yet users differ in their willingness to engage with novel and diverse content.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Results show that the multi-agent system significantly increases Perceived Novelty and Shannon Diversity.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 110. [Pref-CTRL: Preference Driven LLM Alignment using Representation Editing](https://arxiv.org/abs/2604.23543v1)

- 发表时间/状态：2026-04-26；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Test-time alignment methods offer a promising alternative to fine-tuning by steering the outputs of large language models (LLMs) at inference time with lightweight interventions on their internal representations.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Recently, a prominent and effective approach, RE-Control (Kong et al., 2024), has proposed leveraging an external value function trained over the LLM's hidden states to guide generation via gradient-based editing.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 111. [Federated Cross-Modal Retrieval with Missing Modalities via Semantic Routing and Adapter Personalization](https://arxiv.org/abs/2604.22885v1)

- 发表时间/状态：2026-04-24；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Federated cross-modal retrieval faces severe challenges from heterogeneous client data, particularly non-IID semantic distributions and missing modalities.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on MS-COCO, Flickr30K, and other benchmarks show that RCSR consistently improves global retrieval accuracy and training stability, while further enhancing client-level retrieval performance, especially for clients with incomplete modalities.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 112. [How Large Language Models Balance Internal Knowledge with User and Document Assertions](https://arxiv.org/abs/2604.22193v1)

- 发表时间/状态：2026-04-24；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Large language models (LLMs) often need to balance their internal parametric knowledge with external information, such as user beliefs and content from retrieved documents, in real-world scenarios like RAG or chat-based systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Furthermore, our behavioral analysis shows that most models are impressionable, unable to effectively discriminate between helpful and harmful external information.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 113. [Align Generative Artificial Intelligence with Human Preferences: A Novel Large Language Model Fine-Tuning Method for Online Review Management](https://arxiv.org/abs/2604.21209v1)

- 发表时间/状态：2026-04-23；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Online reviews have played a pivotal role in consumers' decision-making processes.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Existing research has highlighted the significant impact of managerial review responses on customer relationship management and firm performance.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 114. [Graph2Counsel: Clinically Grounded Synthetic Counseling Dialogue Generation from Client Psychological Graphs](https://arxiv.org/abs/2604.20382v1)

- 发表时间/状态：2026-04-22；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Rising demand for mental health support has increased interest in using Large Language Models (LLMs) for counseling.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In expert evaluation, our dataset outperforms prior datasets on specificity, counselor competence, authenticity, conversational flow, and safety, with substantial inter-annotator agreement (Krippendorff's $α$ = 0.70).
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 115. [MUSE: Multi-Domain Chinese User Simulation via Self-Evolving Profiles and Rubric-Guided Alignment](https://arxiv.org/abs/2604.13828v1)

- 发表时间/状态：2026-04-15；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：User simulators are essential for the scalable training and evaluation of interactive AI systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We then apply Role-Reversal Supervised Fine-Tuning to improve local response realism and human-like expression.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 116. [AgenticAI-DialogGen: Topic-Guided Conversation Generation for Fine-Tuning and Evaluating Short- and Long-Term Memories of LLMs](https://arxiv.org/abs/2604.12179v1)

- 发表时间/状态：2026-04-14；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Recent advancements in Large Language Models (LLMs) have improved their ability to process extended conversational contexts, yet fine-tuning and evaluating short- and long-term memories remain difficult due to the absence of datasets that encode both short- and long-term conversational history.
- 数据集：TGC
- 主要结论：主要结论可从摘要中的结果句概括为：Recent advancements in Large Language Models (LLMs) have improved their ability to process extended conversational contexts, yet fine-tuning and evaluating short- and long-term memories remain difficult due to the absence of datasets that encode both short- and long-term conversational history.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 117. [LLM-HYPER: Generative CTR Modeling for Cold-Start Ad Personalization via LLM-Based Hypernetworks](https://arxiv.org/abs/2604.12096v1)

- 发表时间/状态：2026-04-13；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：On online advertising platforms, newly introduced promotional ads face the cold-start problem, as they lack sufficient user feedback for model training.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive offline experiments show that LLM-HYPER significantly outperforms cold-start baselines in NDCG$@10$ by 55.9\%.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 118. [Mitigating LLM biases toward spurious social contexts using direct preference optimization](https://arxiv.org/abs/2604.02585v2)

- 发表时间/状态：2026-04-02；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：LLMs are increasingly used for high-stakes decision-making, yet their sensitivity to spurious contextual information can introduce harmful biases.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Applied to Llama 3B \& 8B and Qwen 3B \& 7B Instruct models, Debiasing-DPO reduces bias by 84\% and improves predictive accuracy by 52\% on average.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 119. [MemFactory: Unified Inference & Training Framework for Agent Memory](https://arxiv.org/abs/2603.29493v4)

- 发表时间/状态：2026-03-31；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Memory-augmented Large Language Models (LLMs) are essential for developing capable, long-term AI agents.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Across the evaluation sets, MemFactory improves performance over the corresponding base models on average, with relative gains of up to 14.8%.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 120. [Deploying Semantic ID-based Generative Retrieval for Large-Scale Podcast Discovery at Spotify](https://arxiv.org/abs/2603.17540v1)

- 发表时间/状态：2026-03-18；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Podcast listening is often grounded in a set of favorite shows, while listener intent can evolve over time.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Podcast listening is often grounded in a set of favorite shows, while listener intent can evolve over time.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 121. [12 Angry AI Agents: Evaluating Multi-Agent LLM Decision-Making Through Cinematic Jury Deliberation](https://arxiv.org/abs/2605.01986v1)

- 发表时间/状态：2026-05-03；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：What if the twelve jurors of Sidney Lumet's 12 Angry Men (1957) were not men, but large language models?
- 数据集：MIND
- 主要结论：主要结论可从摘要中的结果句概括为：The work is framed as an exploratory study and discusses implications for jury-of-LLMs evaluation and multi-agent debate.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 122. [SwiftPie: Lightning-fast Subject-driven Image Personalization via One step Diffusion](https://arxiv.org/abs/2605.01510v1)

- 发表时间/状态：2026-05-02；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Diffusion models have achieved remarkable success in high-quality image synthesis, sparking interest in image-guided generation tasks such as subject-driven image personalization.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Diffusion models have achieved remarkable success in high-quality image synthesis, sparking interest in image-guided generation tasks such as subject-driven image personalization.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 123. [ArguMath: AI-Simulated Environment for Pre-Service Teacher Training in Orchestrating Classroom Mathematics Argumentation](https://arxiv.org/abs/2604.22205v1)

- 发表时间/状态：2026-04-24；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：Facilitating productive mathematical argumentation, especially asking rational questions, is essential yet remains challenging for pre-service mathematics teachers (PMTs), who often have limited opportunities to apply abstract theoretical knowledge in authentic practice.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Results from an exploratory user study with seven PMTs, complemented by interviews with four experienced teachers, indicate that ArguMath has the potential to support PMTs' classroom orchestration skills, particularly theory-aligned questioning strategies.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。

### 124. [Behavioral Canaries: Auditing Private Retrieved Context Usage in RL Fine-Tuning](https://arxiv.org/abs/2604.22191v1)

- 发表时间/状态：2026-04-24；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。 摘要中的问题陈述是：In agentic workflows, LLMs frequently process retrieved contexts that are legally protected from further training.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While standard auditing relies on verbatim memorization and membership inference, these methods are ineffective for RL-trained models, as RL primarily influences a model's behavioral style rather than the retention of specific facts.
- 与 LaMP/OPPU 的关系：方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。


## Memory and Dynamic User Modeling

这个方向把个性化看作持续交互中的状态维护问题。早期 profile 多是离线静态文本，近一年工作更强调长期记忆写入、遗忘、冲突解决、时序偏好漂移和可解释调用。它与 agent 和 RAG 紧密相连：记忆既是检索库，也是决策状态。

### 125. [TSUBASA: Improving Long-Horizon Personalization via Evolving Memory and Self-Learning with Context Distillation](https://arxiv.org/abs/2604.07894v1)

- 发表时间/状态：2026-04-09；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。 摘要中的问题陈述是：Personalized large language models (PLLMs) have garnered significant attention for their ability to align outputs with individual's needs and preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Personalized large language models (PLLMs) have garnered significant attention for their ability to align outputs with individual's needs and preferences.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 126. [HingeMem: Boundary Guided Long-Term Memory with Query Adaptive Retrieval for Scalable Dialogues](https://arxiv.org/abs/2604.06845v1)

- 发表时间/状态：2026-04-08；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。 摘要中的问题陈述是：Long-term memory is critical for dialogue systems that support continuous, sustainable, and personalized interactions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments across LLM scales (from 0.6B to production-tier models; \textit{e.g.}, Qwen3-0.6B to Qwen-Flash) on LOCOMO show that HingeMem achieves approximately $20\%$ relative improvement over strong baselines without query categories specification, while reducing computational cost (68\%$\downarrow$ question answering token cost compared to HippoRAG2).
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 127. [Measuring What Makes You Unique: Difference-Aware User Modeling for Enhancing LLM Personalization](https://openreview.net/forum?id=u39h27OyYA)

- 发表时间/状态：2025-03-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。 摘要中的问题陈述是：Personalizing Large Language Models (LLMs) has become a critical step in facilitating their widespread application to enhance individual life experiences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on real-world datasets demonstrate that DPL significantly enhances LLM personalization.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 128. [A Semantic Autonomy Framework for VLM-Integrated Indoor Mobile Robots: Hybrid Deterministic Reasoning and Cross-Robot Adaptive Memory](https://arxiv.org/abs/2605.02525v1)

- 发表时间/状态：2026-05-04；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。 摘要中的问题陈述是：Autonomous indoor mobile robots can navigate reliably to metric coordinates using established frameworks such as ROS 2 Navigation 2, yet they lack the ability to interpret natural language instructions that express intent rather than positions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental validation on two custom-built differential-drive robots across 82 scenario-level decisions and three sessions demonstrates 100% semantic transfer accuracy (33/33, 95% CI [0.894, 1.000]), 100% semantic resolution accuracy, and concurrent multi-robot operation feasibility - all on Raspberry Pi 5 platforms with no onboard GPU, requiring zero training data.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 129. [MEMCoder: Multi-dimensional Evolving Memory for Private-Library-Oriented Code Generation](https://arxiv.org/abs/2604.24222v1)

- 发表时间/状态：2026-04-27；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。 摘要中的问题陈述是：Large Language Models (LLMs) excel at general code generation, but their performance drops sharply in enterprise settings that rely on internal private libraries absent from public pre-training corpora.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive evaluations on the NdonnxEval and NumbaEval benchmarks demonstrate that MEMCoder substantially enhances existing RAG systems, yielding an average absolute pass@1 gain of 16.31%.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 130. [Spatial Metaphors for LLM Memory: A Critical Analysis of the MemPalace Architecture](https://arxiv.org/abs/2604.21284v1)

- 发表时间/状态：2026-04-23；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。 摘要中的问题陈述是：MemPalace is an open-source AI memory system that applies the ancient method of loci (memory palace) spatial metaphor to organize long-term memory for large language models; launched in April 2026, it accumulated over 47,000 GitHub stars in its first two weeks and claims state-of-the-art retrieval performance on the LongMemEval benchmark (96.6% Recall@5) without requiring any LLM inference at write time.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：MemPalace is an open-source AI memory system that applies the ancient method of loci (memory palace) spatial metaphor to organize long-term memory for large language models; launched in April 2026, it accumulated over 47,000 GitHub stars in its first two weeks and claims state-of-the-art retrieval performance on the LongMemEval benchmark (96.6% Recall@5) without requiring any LLM inference at write time.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。


## Personalized Alignment and Preference Learning

这个方向把用户差异推入对齐阶段，研究个体化 reward、DPO/RLHF、偏好聚合和多目标冲突。相较 OPPU 的任务适配，它更关心“不同用户认为好答案的标准不同”。最新进展集中在个体 reward 模型、联邦/私有偏好优化、跨域偏好泛化和避免过度迎合。

### 131. [ALIGN: Prompt-based Attribute Alignment for Reliable, Responsible, and Personalized LLM-based Decision-Making](https://openreview.net/forum?id=iQptQH12zD)

- 发表时间/状态：2025-05-29；ICML 2025 R2-FM Workshop Poster / public_note
- 重要性与相关性：core；score=20
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large language models (LLMs) are increasingly being used as decision aids.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The entire ALIGN framework is open source and will enable new research on reliable, responsible, and personalized LLM-based decision-makers.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 132. [PersonaAgent: When Large Language Model Agents Meet Personalization at Test Time](https://openreview.net/forum?id=fgCOkyJG3f)

- 发表时间/状态：2025-09-02；MTI-LLM @ NeurIPS 2025 Poster / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large Language Model (LLM)-powered agents have emerged as a new paradigm for complex, multi-turn human-AI interactions, yet most existing systems adopt a one-size-fits-all approach, neglecting the evolving preferences and goals of individual users.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental evaluations demonstrate that PersonaAgent significantly outperforms other baseline methods in diverse multi-turn scenarios and demonstrate scaling law in test-time user preference alignment.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 133. [Adaptive Preference Arithmetic: A Personalized Agent with Adaptive Preference Arithmetic for Dynamic Preference Modeling](https://openreview.net/forum?id=gkG8JOOUF4)

- 发表时间/状态：2025-05-08；NeurIPS 2025 poster / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：As large language models (LLMs) are increasingly used as personalized user assistants, effectively adapting to users' evolving preferences is critical for delivering high-quality personalized responses.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：As large language models (LLMs) are increasingly used as personalized user assistants, effectively adapting to users' evolving preferences is critical for delivering high-quality personalized responses.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 134. [GAAMA: Graph Augmented Associative Memory for Agents](https://arxiv.org/abs/2603.27910v1)

- 发表时间/状态：2026-03-29；arXiv / preprint
- 重要性与相关性：core；score=18
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：AI agents that interact with users across multiple sessions require persistent long-term memory to maintain coherent, personalized behavior.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：On the LoCoMo-10 benchmark (1,540 questions across 10 multi-session conversations), GAAMA achieves 78.9\% mean reward, outperforming a tuned RAG baseline (75.0\%), HippoRAG (69.9\%), A-Mem (47.2\%), and Nemori (52.1\%).
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 135. [PersonaVLM: Long-Term Personalized Multimodal LLMs](https://arxiv.org/abs/2604.13074v1)

- 发表时间/状态：2026-03-20；arXiv / preprint
- 重要性与相关性：core；score=18
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Multimodal Large Language Models (MLLMs) serve as daily assistants for millions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments validate our method's effectiveness, improving the baseline by 22.4% (Persona-MME) and 9.8% (PERSONAMEM) under a 128k context, while outperforming GPT-4o by 5.2% and 2.0%, respectively.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 136. [Persistent profile information that affects emotional reasoning in LLMs](https://openreview.net/forum?id=u9Qgn8xSx1)

- 发表时间/状态：2026-02-19；OpenReview / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：This paper investigates how user memory (persistent profile information) affects emotional reasoning in LLMs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：system prompt), additional demographic dimensions (wealth, education, disability), error analysis, and a preliminary DPO-based mitigation experiment on small models.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 137. [FSPO: Few-Shot Preference Optimization of Synthetic Preference Data Elicits LLM Personalization to Real Users](https://openreview.net/forum?id=vKLalvhcjz)

- 发表时间/状态：2025-05-22；MoFA Poster / public_note
- 重要性与相关性：core；score=18
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Effective personalization of LLMs is critical for a broad range of user-interfacing applications such as virtual assistants and content curation.
- 数据集：Alpaca
- 主要结论：主要结论可从摘要中的结果句概括为：Effective personalization of LLMs is critical for a broad range of user-interfacing applications such as virtual assistants and content curation.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 138. [Learning How and What to Memorize: Cognition-Inspired Two-Stage Optimization for Evolving Memory](https://arxiv.org/abs/2605.00702v1)

- 发表时间/状态：2026-05-01；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large language model (LLM) agents require long-term user memory for consistent personalization, but limited context windows hinder tracking evolving preferences over long interactions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We evaluate on three personalization memory benchmarks, covering explicit/implicit preference and different sizes and noise, and observe consistent improvements over strong baselines with favorable robustness, transferability, and efficiency.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 139. [Sparse Personalized Text Generation with Multi-Trajectory Reasoning](https://arxiv.org/abs/2604.24996v1)

- 发表时间/状态：2026-04-27；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：As Large Language Models (LLMs) advance, personalization has become a key mechanism for tailoring outputs to individual user needs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, most existing methods rely heavily on dense interaction histories, making them ineffective in cold-start scenarios where such data is sparse or unavailable.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 140. [Agent-Centric Personalized Multiple Clustering with Multi-Modal LLMs](https://openreview.net/forum?id=o6L4LbeTeQ)

- 发表时间/状态：2025-09-18；Submitted to ICLR 2026 / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Personalized multiple clustering aims to generate diverse partitions of a dataset based on different user-specified aspects, rather than a single clustering.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results show that the proposed method achieves NMI scores of 0.9667 and 0.9481 on the Card Order and Card Suits benchmarks, respectively, largely improving the SOTA model by over 140%.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 141. [NextQuill: Causal Preference Modeling for Enhancing LLM Personalization](https://openreview.net/forum?id=xYpVlKMFqv)

- 发表时间/状态：2025-09-17；ICLR 2026 Poster / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Personalizing large language models (LLMs) is increasingly important as they are progressively integrated into real-world applications to support users’ daily lives.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：As such, NextQuill shifts the alignment process toward learning from causal preference effects, facilitating more effective and personalized LLM adaptation.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 142. [Language Model Personalization via Reward Factorization](https://openreview.net/forum?id=iEmv4Icaxr)

- 发表时间/状态：2025-05-18；PUT at ICML 2025 Oral / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Modern large language models (LLMs) are optimized for human-aligned responses using Reinforcement Learning from Human Feedback (RLHF).
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, existing RLHF approaches assume a universal preference model and fail to account for individual user preferences, limiting their effectiveness in personalized applications.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 143. [Fair Agents: Balancing Multistakeholder Alignment in Multi-Agent Personalization Systems](https://arxiv.org/abs/2605.02379v1)

- 发表时间/状态：2026-05-04；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：LLM agents are increasingly used for personalization due to their ability to communicate directly with users in natural language, integrate external knowledge bases, and negotiate with other (possibly human) agents.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We showcase our framework through a tourism use case and discuss possible applications in other domains, such as education and healthcare.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 144. [MindMelody: A Closed-Loop EEG-Driven System for Personalized Music Intervention](https://arxiv.org/abs/2605.01235v1)

- 发表时间/状态：2026-05-02；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Driven by the escalating global burden of mental health conditions, music-based interventions have attracted significant attention as a non-invasive, cost-effective modality for emotion regulation and psychological stress relief.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Driven by the escalating global burden of mental health conditions, music-based interventions have attracted significant attention as a non-invasive, cost-effective modality for emotion regulation and psychological stress relief.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 145. [Virtual Speech Therapist: A Clinician-in-the-Loop AI Speech Therapy Agent for Personalized and Supervised Therapy](https://arxiv.org/abs/2605.01101v1)

- 发表时间/状态：2026-05-01；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：This paper develops Virtual Speech Therapist (VST), an intelligent agent-based platform that streamlines stuttering assessment and delivers customized therapy planning through automated and adaptive AI-driven workflows.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：VST integrates state-of-the-art deep learning-based stuttering classification, and multi-agent large language model (LLM) reasoning to support evidence-based clinical decision-making.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 146. [GenFacet: End-to-End Generative Faceted Search via Multi-Task Preference Alignment in E-Commerce](https://arxiv.org/abs/2603.19665v1)

- 发表时间/状态：2026-03-20；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Faceted search acts as a critical bridge for navigating massive ecommerce catalogs, yet traditional systems rely on static rule-based extraction or statistical ranking, struggling with emerging vocabulary, semantic gaps, and a disconnect between facet selection and underlying retrieval.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Validated on China's largest selfoperated e-commerce platform via rigorous offline evaluations and online A/B tests, GenFacet demonstrated substantial improvements.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 147. [PrLM: Learning Explicit Reasoning for Personalized RAG via Contrastive Reward Optimization](https://openreview.net/forum?id=y4K6cXcMhV)

- 发表时间/状态：2025-08-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Personalized retrieval-augmented generation (RAG) aims to produce user-tailored responses by incorporating retrieved user profiles alongside the input query.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Guided by a contrastively trained personalization reward model, PrLM effectively learns from user responses without requiring annotated reasoning paths.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 148. [MAPS: Motivation-Aware Personalized Search via LLM-Driven Consultation Alignment](https://openreview.net/forum?id=qtt8CP5Q2B)

- 发表时间/状态：2025-03-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Personalized product search aims to retrieve and rank items that match users' preferences and search intent.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Despite their effectiveness, existing approaches typically assume that users' query fully captures their real motivation.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 149. [Personalized Language Modeling from Personalized Human Feedback](https://openreview.net/forum?id=xxBoca28oG)

- 发表时间/状态：2024-10-05；AFM 2024 Poster / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Personalized large language models (LLMs) are designed to tailor responses to individual user preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our empirical results show that personalized LLMs trained using P-RLHF generate content more closely aligned with individual user preferences, outperforming vanilla, non-personalized RLHF across different tasks.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 150. [PAD: Personalized Alignment of LLMs at Decoding-time](https://openreview.net/forum?id=e7AUJpP8bV)

- 发表时间/状态：2024-09-24；ICLR 2025 Poster / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Aligning with personalized preferences, which vary significantly across cultural, educational, and political differences, poses a significant challenge due to the computational costs and data demands of traditional alignment methods.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Aligning with personalized preferences, which vary significantly across cultural, educational, and political differences, poses a significant challenge due to the computational costs and data demands of traditional alignment methods.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 151. [PAD: Personalized Alignment at Decoding-Time](https://openreview.net/forum?id=qM2iRT6IQA)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Aligning with personalized preferences, which vary significantly across cultural, educational, and political differences, poses a significant challenge due to the computational costs and data demands of traditional alignment methods.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Aligning with personalized preferences, which vary significantly across cultural, educational, and political differences, poses a significant challenge due to the computational costs and data demands of traditional alignment methods.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 152. [IceBreaker for Conversational Agents: Breaking the First-Message Barrier with Personalized Starters](https://arxiv.org/abs/2604.18375v1)

- 发表时间/状态：2026-04-20；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Conversational agents, such as ChatGPT and Doubao, have become essential daily assistants for billions of users.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Online A/B tests on one of the world's largest conversational agent products show that IceBreaker improves user active days by +0.184% and click-through rate by +9.425%, and has been deployed in production.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 153. [HopRank: Self-Supervised LLM Preference-Tuning on Graphs for Few-Shot Node Classification](https://arxiv.org/abs/2604.17271v1)

- 发表时间/状态：2026-04-19；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Node classification on text-attributed graphs (TAGs) is a fundamental task with broad applications in citation analysis, social networks, and recommendation systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Current GNN-based approaches suffer from shallow text encoding and heavy dependence on labeled data, limiting their effectiveness in label-scarce settings.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 154. [High-Stakes Personalization: Rethinking LLM Customization for Individual Investor Decision-Making](https://arxiv.org/abs/2604.04300v1)

- 发表时间/状态：2026-04-05；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Personalized LLM systems have advanced rapidly, yet most operate in domains where user preferences are stable and ground truth is either absent or subjective.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We describe the architectural responses that emerged from building the system and propose open research directions for personalized NLP in high-stakes, temporally extended decision domains.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 155. [Many Preferences, Few Policies: Towards Scalable Language Model Personalization](https://arxiv.org/abs/2604.04144v2)

- 发表时间/状态：2026-04-05；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：The holy grail of LLM personalization is a single LLM for each user, perfectly aligned with that user's preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We provide empirical results that validate these guarantees and demonstrate greater output diversity over common baselines.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 156. [Diagnostic-Guided Dynamic Profile Optimization for LLM-based User Simulators in Sequential Recommendation](https://openreview.net/forum?id=7rJuybH0wV)

- 发表时间/状态：2026-01-01；AAAI 2026 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Recent advances in large language models (LLMs) have enabled realistic user simulators for developing and evaluating recommender systems (RSs).
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments conducted on three real-world datasets demonstrate the effectiveness of our proposed framework.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 157. [Aligning to Thousands of Preferences via System Message Generalization](https://openreview.net/forum?id=29PsrhMb3a)

- 发表时间/状态：2024-09-11；Pluralistic-Alignment 2024 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Current large language model (LLM) alignment methods often assume that aligning LLMs with general public preferences is optimal, overlooking individual value diversity.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To improve generalization to diverse system messages, we create a system message dataset with 197k value combinations across 66k user instructions.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 158. [Mallows-DPO: Fine-Tune Your LLM with Preference Dispersions](https://openreview.net/forum?id=rbTu46dkgU)

- 发表时间/状态：2024-09-06；Pluralistic-Alignment 2024 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Direct Preference Optimization (DPO) has recently emerged as a popular approach to improve reinforcement learning with human feedback (RLHF), leading to better techniques to fine-tune large language models (LLM).
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Direct Preference Optimization (DPO) has recently emerged as a popular approach to improve reinforcement learning with human feedback (RLHF), leading to better techniques to fine-tune large language models (LLM).
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 159. [DynamicPO: Dynamic Preference Optimization for Recommendation](https://arxiv.org/abs/2605.00327v1)

- 发表时间/状态：2026-05-01；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：In large language model (LLM)-based recommendation systems, direct preference optimization (DPO) effectively aligns recommendations with user preferences, requiring multi-negative objective functions to leverage abundant implicit-feedback negatives and sharpen preference boundaries.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In large language model (LLM)-based recommendation systems, direct preference optimization (DPO) effectively aligns recommendations with user preferences, requiring multi-negative objective functions to leverage abundant implicit-feedback negatives and sharpen preference boundaries.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 160. [ProMax: Exploring the Potential of LLM-derived Profiles with Distribution Shaping for Recommender Systems](https://arxiv.org/abs/2604.26231v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：The remarkable text understanding and generation capabilities of large language models (LLMs) have revitalized the field of general recommendation based on implicit user feedback.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To address these limitations, we revisit profiles from a retrieval perspective and propose a simple yet effective recommendation framework built upon distribution shaping (ProMax) in this paper.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 161. [HeadRank: Decoding-Free Passage Reranking via Preference-Aligned Attention Heads](https://arxiv.org/abs/2604.17237v1)

- 发表时间/状态：2026-04-19；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Decoding-free reranking methods that read relevance signals directly from LLM attention weights offer significant latency advantages over autoregressive approaches, yet suffer from attention score homogenization: middle-context documents receive near-identical scores, destroying the fine-grained distinctions required for ranking.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Decoding-free reranking methods that read relevance signals directly from LLM attention weights offer significant latency advantages over autoregressive approaches, yet suffer from attention score homogenization: middle-context documents receive near-identical scores, destroying the fine-grained distinctions required for ranking.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 162. [Transparent and Controllable Recommendation Filtering via Multimodal Multi-Agent Collaboration](https://arxiv.org/abs/2604.17459v1)

- 发表时间/状态：2026-04-19；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：While personalized recommender systems excel at content discovery, they frequently expose users to undesirable or discomforting information, highlighting the critical need for user-centric filtering tools.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Evaluated on an adversarial dataset comprising 473 highly confusing samples, the proposed architecture effectively curbed over-association, decreasing the false positive rate by 74.3% and achieving nearly twice the F1-Score of traditional text-only baselines.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 163. [Behavior-Aware Dual-Channel Preference Learning for Heterogeneous Sequential Recommendation](https://arxiv.org/abs/2604.14581v1)

- 发表时间/状态：2026-04-16；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Heterogeneous sequential recommendation (HSR) aims to learn dynamic behavior dependencies from the diverse behaviors of user-item interactions to facilitate precise sequential recommendation.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Despite many efforts yielding promising achievements, there are still challenges in modeling heterogeneous behavior data.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 164. [HARPO: Hierarchical Agentic Reasoning for User-Aligned Conversational Recommendation](https://arxiv.org/abs/2604.10048v1)

- 发表时间/状态：2026-04-11；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Conversational recommender systems (CRSs) operate under incremental preference revelation, requiring systems to make recommendation decisions under uncertainty.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While recent approaches particularly those built on large language models achieve strong performance on standard proxy metrics such as Recall@K and BLEU, they often fail to deliver high-quality, user-aligned recommendations in practice.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 165. [Fusion and Alignment Enhancement with Large Language Models for Tail-item Sequential Recommendation](https://arxiv.org/abs/2604.03688v1)

- 发表时间/状态：2026-04-04；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Sequential Recommendation (SR) learns user preferences from their historical interaction sequences and provides personalized suggestions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Despite previous efforts to leverage LLM-derived embeddings for enriching tail items, they still face the following limitations: 1) They struggle to effectively fuse collaborative signals with semantic knowledge, leading to suboptimal item embedding quality.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 166. [Uncertainty-Aware Variational Reward Factorization via Probabilistic Preference Bases for LLM Personalization](https://arxiv.org/abs/2604.00997v1)

- 发表时间/状态：2026-04-01；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Reward factorization personalizes large language models (LLMs) by decomposing rewards into shared basis functions and user-specific weights.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：On three benchmarks, VRF outperforms all baselines across seen and unseen users, few-shot scenarios, and varying uncertainty levels, with gains extending to downstream alignment.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 167. [Personalized Soups: Personalized Large Language Model Alignment via Post-hoc Parameter Merging](https://openreview.net/forum?id=EMrnoPRvxe)

- 发表时间/状态：2024-09-19；AFM 2024 Oral / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：While Reinforcement Learning from Human Feedback (RLHF) aligns Large Language Models (LLMs) with general, aggregate human preferences, it is suboptimal for learning diverse, individual perspectives.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Compared to strong single-objective baselines, we show that we can achieve personalized alignment by decomposing preferences into multiple dimensions.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 168. [Cognitive Twins: Investigating Personalized Thinking Model Building and Its Performance Enhancement with Human-in-the-Loop](https://arxiv.org/abs/2605.04761v1)

- 发表时间/状态：2026-05-06；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：This paper presents the Personalized Thinking Model (PTM), a hierarchical and interpretable learner representation designed for AI supported education.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Third, semantic alignment verification showed that topic coherence increased from 0.436 at the behavioral layer to 0.626 at the core value layer, while lexical overlap with journal vocabulary decreased from 0.114 to 0.007 across those same layers.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 169. [RLearner-LLM: Balancing Logical Grounding and Fluency in Large Language Models via Hybrid Direct Preference Optimization](https://arxiv.org/abs/2605.04539v1)

- 发表时间/状态：2026-05-06；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Direct Preference Optimization (DPO), the efficient alternative to PPO-based RLHF, falls short on knowledge-intensive generation: standard preference signals from human annotators or LLM judges exhibit a systematic verbosity bias that rewards fluency over logical correctness.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Evaluated across five academic domains (Biology, Medicine, Law) with three base architectures (LLaMA-2-13B, Qwen3-8B, Gemma 4 E4B-it), RLearner-LLM yields up to 6x NLI improvement over SFT, with NLI gains in 11 of 15 cells and consistent answer-coverage gains.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 170. [Feedback-Normalized Developer Memory for Reinforcement-Learning Coding Agents: A Safety-Gated MCP Architecture](https://arxiv.org/abs/2605.01567v1)

- 发表时间/状态：2026-05-02；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large language model (LLM) coding agents increasingly operate over repositories, terminals, tests, and execution traces across long software-engineering episodes.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In the same-commit comparison, deterministic control and full shadow/OPE both achieve 80.0% expected-decision accuracy and 100.0% hard-negative suppression; the full configuration adds learning telemetry rather than accuracy gain.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 171. [TUR-DPO: Topology- and Uncertainty-Aware Direct Preference Optimization](https://arxiv.org/abs/2605.00224v1)

- 发表时间/状态：2026-04-30；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Aligning large language models (LLMs) with human preferences is commonly done via reinforcement learning from human feedback (RLHF) with Proximal Policy Optimization (PPO) or, more simply, via Direct Preference Optimization (DPO).
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Empirically, across open 7-8B models and benchmarks spanning mathematical reasoning, factual question answering, summarization, and helpful/harmless dialogue, TUR-DPO improves judge win-rates, faithfulness, and calibration relative to DPO while preserving training simplicity and avoiding online rollouts.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 172. [Intrinsic Mutual Information as a Modulator for Preference Optimization](https://arxiv.org/abs/2604.24804v1)

- 发表时间/状态：2026-04-27；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Offline preference optimization methods, such as Direct Preference Optimization (DPO), offer significant advantages in aligning Large Language Models (LLMs) with human values.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Offline preference optimization methods, such as Direct Preference Optimization (DPO), offer significant advantages in aligning Large Language Models (LLMs) with human values.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 173. [PREF-XAI: Preference-Based Personalized Rule Explanations of Black-Box Machine Learning Models](https://arxiv.org/abs/2604.19684v1)

- 发表时间/状态：2026-04-21；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Explainable artificial intelligence (XAI) has predominantly focused on generating model-centric explanations that approximate the behavior of black-box models.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results on real-world datasets show that PREF-XAI can accurately reconstruct user preferences from limited feedback, identify highly relevant explanations, and discover novel explanatory rules not initially considered by the user.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 174. [DeltaMem: Towards Agentic Memory Management via Reinforcement Learning](https://arxiv.org/abs/2604.01560v1)

- 发表时间/状态：2026-04-02；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Recent advances in persona-centric memory have revealed the powerful capability of multi-agent systems in managing persona memory, especially in conversational scenarios.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To further improve the performance of our agentic memory manager, we draw inspiration from the evolution of human memory and synthesize a user-assistant dialogue dataset along with corresponding operation-level memory updating labels.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 175. [Multi-Agent Video Recommenders: Evolution, Patterns, and Open Challenges](https://arxiv.org/abs/2604.02211v1)

- 发表时间/状态：2026-04-02；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Video recommender systems are among the most popular and impactful applications of AI, shaping content consumption and influencing culture for billions of users.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We also outline open challenges in scalability, multimodal understanding, incentive alignment, and identify research directions such as hybrid reinforcement learning-LLM systems, lifelong personalization and self-improving recommender systems.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 176. [Aligning Multimodal Sequential Recommendations via Robust Direct Preference Optimization with Sparse MoE](https://arxiv.org/abs/2603.29259v1)

- 发表时间/状态：2026-03-31；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Preference-based alignment objectives have been widely adopted, from RLHF-style pairwise learning in large language models to emerging applications in recommender systems.
- 数据集：Amazon
- 主要结论：主要结论可从摘要中的结果句概括为：Our central finding is that a simple modification, replacing deterministic hard negatives with stochastic sampling from a dynamic top-K candidate pool, consistently improves ranking performance.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 177. [Causal Direct Preference Optimization for Distributionally Robust Generative Recommendation](https://arxiv.org/abs/2603.22335v1)

- 发表时间/状态：2026-03-21；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Direct Preference Optimization (DPO) guides large language models (LLMs) to generate recommendations aligned with user historical behavior distributions by minimizing preference alignment loss.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, our systematic empirical research and theoretical analysis reveal that DPO tends to amplify spurious correlations caused by environmental confounders during the alignment process, significantly undermining the generalization capability of LLM-based generative recommendation methods in out of distribution (OOD) scenarios.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 178. [EduAgentQG: A Multi-Agent Workflow Framework for Personalized Question Generation](https://openreview.net/forum?id=LGJAjWxy5S)

- 发表时间/状态：2025-11-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：High-quality personalized question banks are crucial for supporting adaptive learning and individualized assessment.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Manually designing questions is time-consuming and often fails to meet diverse learning needs, making automated question generation a crucial approach to reduce teachers' workload and improve the scalability of educational resources.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 179. [PAL: Pluralistic Alignment Framework for Learning from Heterogeneous Preferences](https://openreview.net/forum?id=cxBLcw64xq)

- 发表时间/状态：2024-09-09；Pluralistic-Alignment 2024 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large foundation models require extensive \textit{alignment} to human preferences before deployment.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：With simple multi-layer perceptron, PAL achieves competitive reward model accuracy on Summary \cite{stiennon2020learning} (language), Pick-a-Pic \cite{kirstain2024pick} (image generation), and Persona \cite{perez2022discovering} (semi-synthetic) heterogeneous preference datasets, matching state-of-the-art performance with greater efficiency.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 180. [Beyond Static Best-of-N: Bayesian List-wise Alignment for LLM-based Recommendation](https://arxiv.org/abs/2605.04559v1)

- 发表时间/状态：2026-05-06；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large Language Models have revolutionized recommender systems (LLM4Rec) by leveraging their generative capabilities to model complex user preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To address this, BoN Alignment aims to distill the search capability into the model itself, yet current approaches suffer from two critical limitations: (1) Indiscriminate Supervision, where the static reference fails to distinguish the relative quality of candidates exceeding its empirical range, leading to a loss of ranking guidance; and (2) Gradient Decay, where the effective supervision signal rapidly diminishes as the evolving policy improves, resulting in inefficient optimization.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 181. [Misaligned by Reward: Socially Undesirable Preferences in LLMs](https://arxiv.org/abs/2605.05003v1)

- 发表时间/状态：2026-05-06；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Reward models are a key component of large language model alignment, serving as proxies for human preferences during training.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：These findings show that standard reward benchmarks are insufficient for assessing social alignment and highlight the need for evaluations that directly measure the social preferences encoded in reward models.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 182. [Gradient-Gated DPO: Stabilizing Preference Optimization in Language Models](https://arxiv.org/abs/2605.02626v1)

- 发表时间/状态：2026-05-04；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Preference optimization has become a central paradigm for aligning large language models with human feedback.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, recent work shows that DPO exhibits a squeezing effect, where negative gradients applied to rejected responses concentrate probability mass on high-confidence predictions while suppressing alternative responses.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 183. [Learning When to Remember: Risk-Sensitive Contextual Bandits for Abstention-Aware Memory Retrieval in LLM-Based Coding Agents](https://arxiv.org/abs/2604.27283v1)

- 发表时间/状态：2026-04-30；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large language model (LLM)-based coding agents increasingly rely on external memory to reuse prior debugging experience, repair traces, and repository-local operational knowledge.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The results show that, for coding-agent memory, the key question is not only which memory is most similar, but whether any retrieved memory is safe enough to influence the debugging trajectory.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 184. [Factorized Latent Reasoning for LLM-based Recommendation](https://arxiv.org/abs/2604.26760v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Large language models (LLMs) have recently been adopted for recommendation by framing user preference modeling as a language generation problem.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on multiple benchmarks show that FLR consistently outperforms strong baselines while improving robustness and interpretability.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 185. [Toward Personalized Digital Twins for Cognitive Decline Assessment: A Multimodal, Uncertainty-Aware Framework](https://arxiv.org/abs/2604.27217v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Cognitive decline is highly heterogeneous across individuals, which complicates prognosis, trial design, and treatment planning.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：As a preliminary feasibility study, we analyze longitudinal TADPOLE trajectories and show clear separation between cognitively normal and Alzheimer's disease cohorts in ADAS13, ventricle volume, and hippocampal volume over five years.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 186. [LLMs Reading the Rhythms of Daily Life: Aligned Understanding for Behavior Prediction and Generation](https://arxiv.org/abs/2604.23578v1)

- 发表时间/状态：2026-04-26；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：Human daily behavior unfolds as complex sequences shaped by intentions, preferences, and context.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Effectively modeling these behaviors is crucial for intelligent systems such as personal assistants and recommendation engines.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 187. [Quantifying and Mitigating Self-Preference Bias of LLM Judges](https://arxiv.org/abs/2604.22891v2)

- 发表时间/状态：2026-04-24；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：LLM-as-a-Judge has become a dominant approach in automated evaluation systems, playing critical roles in model alignment, leaderboard construction, quality control, and so on.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To mitigate this bias, we propose a structured multi-dimensional evaluation strategy grounded in cognitive load decomposition, which reduces SPB by 31.5\% on average.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 188. [Dialect vs Demographics: Quantifying LLM Bias from Implicit Linguistic Signals vs. Explicit User Profiles](https://arxiv.org/abs/2604.21152v1)

- 发表时间/状态：2026-04-22；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。 摘要中的问题陈述是：As state-of-the-art Large Language Models (LLMs) have become ubiquitous, ensuring equitable performance across diverse demographics is critical.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：As state-of-the-art Large Language Models (LLMs) have become ubiquitous, ensuring equitable performance across diverse demographics is critical.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。


## Personalized Agents and Assistants

这个方向关注长期助手如何理解个人目标、工作流和工具偏好。与单次文本生成不同，agent 个性化需要在规划、调用工具、记忆更新和任务复盘中保持一致。最新工作通常把用户模型、记忆、反馈和环境状态合在一起，评估也更偏向真实任务完成度。

### 189. [Adaptive Friend Agent: Personalized Multi-User Memory for Conversational AI](https://openreview.net/forum?id=wKTwm7ZzDK)

- 发表时间/状态：2025-09-19；Submitted to ICLR 2026 / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Most conversational AI systems today are designed to engage a single user, which limits their effectiveness in real-world, multi-user settings.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Most conversational AI systems today are designed to engage a single user, which limits their effectiveness in real-world, multi-user settings.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 190. [A Survey of Personalization: From RAG to Agent](https://openreview.net/forum?id=i7qbfjGQ2B)

- 发表时间/状态：2025-04-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Personalization has become an essential capability in modern AI systems, enabling customized interactions that align with individual user preferences, contexts, and goals.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Relevant papers and resources are continuously updated at https://github.com/Applied-Machine-Learning-Lab/Awesome-Personalized-RAG-Agent.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 191. [Trojan Hippo: Weaponizing Agent Memory for Data Exfiltration](https://arxiv.org/abs/2605.01970v2)

- 发表时间/状态：2026-05-03；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Memory systems enable otherwise-stateless LLM agents to persist user information across sessions, but also introduce a new attack surface.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Instantiated on an email assistant across four memory backends (explicit tool memory, agentic memory, RAG, and sliding-window context), Trojan Hippo achieves up to 85-100% ASR against current frontier models from OpenAI and Google, with planted memories successfully activating even after 100 benign sessions.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 192. [Synthius-Mem: Brain-Inspired Hallucination-Resistant Persona Memory Achieving 94.4% Memory Accuracy and 99.6% Adversarial Robustness on LoCoMo](https://arxiv.org/abs/2604.11563v1)

- 发表时间/状态：2026-04-13；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Providing AI agents with reliable long-term memory that does not hallucinate remains an open problem.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：On the LoCoMo benchmark (ACL 2024, 10 conversations, 1,813 questions), Synthius-Mem achieves 94.37% accuracy, exceeding all published systems including MemMachine (91.69%, adversarial score is not reported) and human performance (87.9 F1).
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 193. [HyperMem: Hypergraph Memory for Long-Term Conversations](https://arxiv.org/abs/2604.08256v2)

- 发表时间/状态：2026-04-09；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Long-term memory is essential for conversational agents to maintain coherence, track persistent tasks, and provide personalized interactions across extended dialogues.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on the LoCoMo benchmark show that HyperMem achieves state-of-the-art performance with 92.73% LLM-as-a-judge accuracy, demonstrating the effectiveness of HyperMem for long-term conversations.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 194. [Personalized Vehicular Health Diagnosis via Large Language Model](https://openreview.net/forum?id=QKsoes5Jrc)

- 发表时间/状态：2026-04-06；IEEE Communications Standards Magazine / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：In the past decade, vehicle on-board diagnostics (OBD) systems have significantly improved by leveraging numerous electronic control units (ECUs) to monitor a wide array of real-time sensor data and report faults.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In the past decade, vehicle on-board diagnostics (OBD) systems have significantly improved by leveraging numerous electronic control units (ECUs) to monitor a wide array of real-time sensor data and report faults.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 195. [Agentic AI for Personalized Physiotherapy: A Multi-Agent Framework for Generative Video Training and Real-Time Pose Correction](https://arxiv.org/abs/2604.21154v1)

- 发表时间/状态：2026-04-22；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：At-home physiotherapy compliance remains critically low due to a lack of personalized supervision and dynamic feedback.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This work demonstrates the feasibility of combining generative media with agentic autonomous decision-making to scale personalized patient care safely and effectively.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 196. [Can Virtual Agents Care? Designing an Empathetic and Personalized LLM-Driven Conversational Agent](https://arxiv.org/abs/2604.20948v1)

- 发表时间/状态：2026-04-22；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Mental health challenges are rising globally, while traditional support services face limited availability and high costs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Objective benchmarks demonstrate improved retrieval and response quality, particularly for smaller models.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 197. [SteerX: Disentangled Steering for LLM Personalization](https://openreview.net/forum?id=ojtQ5kEYIn)

- 发表时间/状态：2025-10-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Large language models (LLMs) have shown remarkable success in recent years, enabling a wide range of applications, including intelligent assistants that support users' daily life and work.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large language models (LLMs) have shown remarkable success in recent years, enabling a wide range of applications, including intelligent assistants that support users' daily life and work.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 198. [Multitask Asynchronous Bidirectional Multimodal Agent for Personalized Treatment Companions](https://openreview.net/forum?id=Cwz0l16Lk4)

- 发表时间/状态：2025-09-07；NeurIPS 2025 2nd Workshop FM4LS Poster / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Personalized treatment requires intelligent systems that can continuously monitor patients, adapt to evolving conditions, and communicate naturally with both patients and clinicians.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In this work, we demonstrated a Multitask Asynchronous Bidirectional Multimodal Agent powered by a multimodal large language model (MLLM) and integrated with retrieval-augmented generation (RAG) from multimodal sources, including text, images, and video.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 199. [MemORAI: Memory Organization and Retrieval via Adaptive Graph Intelligence for LLM Conversational Agents](https://arxiv.org/abs/2605.01386v1)

- 发表时间/状态：2026-05-02；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Large Language Models (LLMs) lack persistent memory for long-term personalized conversations.
- 数据集：LOCOMO and LongMemEval
- 主要结论：主要结论可从摘要中的结果句概括为：Evaluated on LOCOMO and LongMemEval benchmarks, MemORAI achieves state-of-the-art performance in memory retrieval and personalized response generation, demonstrating that selective storage, enriched representation, and adaptive retrieval are essential for coherent, personalized LLM agents.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 200. [M2HRI: An LLM-Driven Multimodal Multi-Agent Framework for Personalized Human-Robot Interaction](https://arxiv.org/abs/2604.11975v1)

- 发表时间/状态：2026-04-13；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Multi-robot systems hold significant promise for social environments such as homes and hospitals, yet existing multi-robot works treat robots as functionally identical, overlooking how robots individual identity shape user perception and how coordination shapes multi-robot behavior when such individuality is present.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Multi-robot systems hold significant promise for social environments such as homes and hospitals, yet existing multi-robot works treat robots as functionally identical, overlooking how robots individual identity shape user perception and how coordination shapes multi-robot behavior when such individuality is present.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 201. [Memory as Metabolism: A Design for Companion Knowledge Systems](https://arxiv.org/abs/2604.12034v1)

- 发表时间/状态：2026-04-13；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Retrieval-Augmented Generation remains the dominant pattern for giving LLMs persistent memory, but a visible cluster of personal wiki-style memory architectures emerged in April 2026 -- design proposals from Karpathy, MemPalace, and LLM Wiki v2 that compile knowledge into an interlinked artifact for long-term use by a single user.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The safety story at the single-agent level is partial, and the paper is explicit about what it does and does not solve.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 202. [Chronos: Temporal-Aware Conversational Agents with Structured Event Retrieval for Long-Term Memory](https://arxiv.org/abs/2603.16862v1)

- 发表时间/状态：2026-03-17；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Recent advances in Large Language Models (LLMs) have enabled conversational AI agents to engage in extended multi-turn interactions spanning weeks or months.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, existing memory systems struggle to reason over temporally grounded facts and preferences that evolve across months of interaction and lack effective retrieval strategies for multi-hop, time-sensitive queries over long dialogue histories.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 203. [Collaborative Memory: Multi-User Memory Sharing in LLM Agents with Dynamic Access Control](https://openreview.net/forum?id=pJUQ5YA98Z)

- 发表时间/状态：2025-09-19；Submitted to ICLR 2026 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Complex tasks are increasingly delegated to ensembles of specialized LLM-based agents that reason, communicate, and coordinate actions—both among themselves and through interactions with external tools, APIs, and databases.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While persistent memory has been shown to enhance single-agent performance, most approaches assume a monolithic, single-user context—overlooking the benefits and challenges of knowledge transfer across users under dynamic, asymmetric permissions.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 204. [GRAVITY: Architecture-Agnostic Structured Anchoring for Long-Horizon Conversational Memory](https://arxiv.org/abs/2605.01688v1)

- 发表时间/状态：2026-05-03；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Long-horizon conversational agents rely on memory systems with increasingly sophisticated retrieval mechanisms.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This approach effectively synthesizes scattered evidence into a coherent, query-relevant context without requiring any architectural modifications to the host model.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 205. [Detecting Clinical Discrepancies in Health Coaching Agents: A Dual-Stream Memory and Reconciliation Architecture](https://arxiv.org/abs/2604.27045v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：As Large Language Model (LLM) agents transition from single-session tools to persistent systems managing longitudinal healthcare journeys, their memory architectures face a critical challenge: reconciling two imperfect sources of truth.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：These findings establish that validating patient-reported memories against clinical records is both feasible and necessary for safe deployment of longitudinal health agents.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 206. [From Feelings to Metrics: Understanding and Formalizing How Users Vibe-Test LLMs](https://arxiv.org/abs/2604.14137v2)

- 发表时间/状态：2026-04-15；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Evaluating LLMs is challenging, as benchmark scores often fail to capture models' real-world usefulness.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：These findings suggest that formalized vibe-testing can serve as a useful approach for bridging benchmark scores and real-world experience.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 207. [Thought-Retriever: Don't Just Retrieve Raw Data, Retrieve Thoughts for Memory-Augmented Agentic Systems](https://arxiv.org/abs/2604.12231v1)

- 发表时间/状态：2026-04-14；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Large language models (LLMs) have transformed AI research thanks to their powerful internal capabilities and knowledge.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, existing LLMs still fail to effectively incorporate the massive external knowledge when interacting with the world.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 208. [Mathematics Teachers Interactions with a Multi-Agent System for Personalized Problem Generation](https://arxiv.org/abs/2604.12066v1)

- 发表时间/状态：2026-04-13；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Large language models can increasingly adapt educational tasks to learners characteristics.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Implications for multi-agent systems for personalization that support teacher control are given.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 209. [Cognis: Context-Aware Memory for Conversational AI Agents](https://arxiv.org/abs/2604.19771v1)

- 发表时间/状态：2026-03-27；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：LLM agents lack persistent memory, causing conversations to reset each session and preventing personalization over time.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We evaluate Cognis on two independent benchmarks -- LoCoMo and LongMemEval -- across eight answer generation models, demonstrating state-of-the-art performance on both.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 210. [EgoSelf: From Memory to Personalized Egocentric Assistant](https://arxiv.org/abs/2604.19564v2)

- 发表时间/状态：2026-04-21；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Egocentric assistants often rely on first-person view data to capture user behavior and context for personalized services.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Since different users exhibit distinct habits, preferences, and routines, such personalization is essential for truly effective assistance.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 211. [Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints](https://arxiv.org/abs/2604.17979v1)

- 发表时间/状态：2026-04-20；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：The rapid adoption of artificial intelligence (AI) and large language models (LLMs) is transforming financial analytics by enabling natural language interfaces for reporting, decision support, and automated reasoning.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Results reveal a consistent architectural inversion: structured memory improves precision in deterministic, operand-explicit tasks, while retrieval-based approaches outperform memory-centric methods in conversational, reference-implicit settings.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 212. [HeLa-Mem: Hebbian Learning and Associative Memory for LLM Agents](https://arxiv.org/abs/2604.16839v1)

- 发表时间/状态：2026-04-18；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Long-term memory is a critical challenge for Large Language Model agents, as fixed context windows cannot preserve coherence across extended interactions.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on LoCoMo demonstrate superior performance across four question categories while using significantly fewer context tokens.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 213. [Preference Estimation via Opponent Modeling in Multi-Agent Negotiation](https://arxiv.org/abs/2604.15687v1)

- 发表时间/状态：2026-04-17；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Automated negotiation in complex, multi-party and multi-issue settings critically depends on accurate opponent modeling.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results on a multi-party benchmark demonstrate that our framework improves the full agreement rate and preference estimation accuracy by integrating probabilistic reasoning with natural language understanding.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 214. [MemReader: From Passive to Active Extraction for Long-Term Agent Memory](https://arxiv.org/abs/2604.07877v2)

- 发表时间/状态：2026-04-09；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Long-term memory is fundamental for personalized and autonomous agents, yet populating it remains a bottleneck.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on LOCOMO, LongMemEval, and HaluMem show that MemReader consistently outperforms existing extraction-based baselines.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 215. [ColorEcosystem: Powering Personalized, Standardized, and Trustworthy Agentic Service in massive-agent Ecosystem](https://openreview.net/forum?id=Vxm7SrHm9V)

- 发表时间/状态：2025-10-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：With the rapid development of (multimodal) large language model-based agents, the landscape of agentic service management has evolved from single-agent systems to multi-agent systems, and now to massive-agent ecosystems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Meanwhile, we have also implemented part of ColorEcosystem's functionality, and the relevant code is open-sourced at https://github.com/opas-lab/color-ecosystem.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 216. [A Low-Code Approach for the Automatic Personalization of Conversational Agents](https://arxiv.org/abs/2605.02384v1)

- 发表时间/状态：2026-05-04；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：In this paper, we conducted an SLR on the state of user modeling in the MDE domain.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Results show a diverse set of disconnected proposals, covering a partial number of dimensions with an emphasis on those characteristics that are easier to profile.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 217. [DRACULA: Hunting for the Actions Users Want Deep Research Agents to Execute](https://arxiv.org/abs/2604.23815v1)

- 发表时间/状态：2026-04-26；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Scientific Deep Research (DR) agents answer user queries by synthesizing research papers into multi-section reports.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：User feedback can improve their utility, but existing protocols only score the final report, making it hard to study and learn which intermediate actions DR agents should take to improve reports.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 218. [Cooperative Profiles Predict Multi-Agent LLM Team Performance in AI for Science Workflows](https://arxiv.org/abs/2604.20658v1)

- 发表时间/状态：2026-04-22；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Multi-agent systems built from teams of large language models (LLMs) are increasingly deployed for collaborative scientific reasoning and problem-solving.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Here, we benchmark 35 open-weight LLMs across six behavioral economics games and show that game-derived cooperative profiles robustly predict downstream performance in AI-for-Science tasks, where teams of LLM agents collaboratively analyze data, build models, and produce scientific reports under shared budget constraints.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 219. [Dual-Cluster Memory Agent: Resolving Multi-Paradigm Ambiguity in Optimization Problem Solving](https://arxiv.org/abs/2604.20183v1)

- 发表时间/状态：2026-04-22；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。 摘要中的问题陈述是：Large Language Models (LLMs) often struggle with structural ambiguity in optimization problems, where a single problem admits multiple related but conflicting modeling paradigms, hindering effective solution generation.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large Language Models (LLMs) often struggle with structural ambiguity in optimization problems, where a single problem admits multiple related but conflicting modeling paradigms, hindering effective solution generation.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。


## LLM-based Recommendation and Ranking

这个方向是个性化 LLM 与推荐系统交汇处：LLM 被用来理解用户历史、生成解释、做 conversational recommendation，或作为排序/重排模型。发展脉络从把 LLM 当语义编码器，走向利用自然语言偏好、生成式用户模拟和多轮交互。最新进展关注冷启动、可解释性、长序列行为和推荐中的对齐风险。

### 220. [User Behavior Simulation with Large Language Model-based Agents](https://openreview.net/forum?id=tJvZDb5GsT)

- 发表时间/状态：2024-12-20；Crossref / public_note
- 重要性与相关性：core；score=19
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Simulating high quality user behavior data has always been a fundamental yet challenging problem in human-centered applications such as recommendation systems, social networks, among many others.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Recently, substantial evidence has suggested that by learning huge amounts of web knowledge, large language models (LLMs) can achieve human-like intelligence and generalization capabilities.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 221. [SAGER: Self-Evolving User Policy Skills for Recommendation Agent](https://arxiv.org/abs/2604.14972v2)

- 发表时间/状态：2026-04-16；arXiv / preprint
- 重要性与相关性：core；score=18
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Large language model (LLM) based recommendation agents personalize what they know through evolving per-user semantic memory, yet how they reason remains a universal, static system prompt shared identically across all users.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on four public benchmarks demonstrate that SAGER achieves state-of-the-art performance, with gains orthogonal to memory accumulation, confirming that personalizing the reasoning process itself is a qualitatively distinct source of recommendation improvement.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 222. [LLM-based User Profile Management for Recommender System](https://openreview.net/forum?id=f9nybwvO9X)

- 发表时间/状态：2025-02-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=17
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：The rapid advancement of Large Language Models (LLMs) has opened new opportunities in recommender systems by enabling zero-shot recommendation without conventional training.
- 数据集：Amazon
- 主要结论：主要结论可从摘要中的结果句概括为：Despite their potential, most existing works rely solely on users' purchase histories, leaving significant room for improvement by incorporating user-generated textual data, such as reviews and product descriptions.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 223. [SecMate: Multi-Agent Adaptive Cybersecurity Troubleshooting with Tri-Context Personalization](https://arxiv.org/abs/2604.26394v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Recent advances in large language models and agentic frameworks have enabled virtual customer assistants (VCAs) for complex support.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Service specificity is achieved through a proactive, context-aware recommender.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 224. [GraphRAG-IRL: Personalized Recommendation with Graph-Grounded Inverse Reinforcement Learning and LLM Re-ranking](https://arxiv.org/abs/2604.19128v1)

- 发表时间/状态：2026-04-21；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Personalized recommendation requires models that capture sequential user preferences while remaining robust to sparse feedback and semantic ambiguity.
- 数据集：MovieLens
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments show that GraphRAG-IRL is a strong standalone recommender: IRL-MLP with GraphRAG improves NDCG@10 by 15.7\% on MovieLens and 16.6\% on KuaiRand over supervised baselines.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 225. [ReFORM: Review-aggregated Profile Generation via LLM with Multi-Factor Attention for Restaurant Recommendation](https://arxiv.org/abs/2603.16236v1)

- 发表时间/状态：2026-03-17；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：In recommender systems, large language models (LLMs) have gained popularity for generating descriptive summarization to improve recommendation robustness, along with Graph Convolution Networks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In recommender systems, large language models (LLMs) have gained popularity for generating descriptive summarization to improve recommendation robustness, along with Graph Convolution Networks.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 226. [Learning from Personal Preferences](https://openreview.net/forum?id=h56z6J7UsN)

- 发表时间/状态：2024-09-08；Pluralistic-Alignment 2024 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Machine learning practitioners frequently use majority vote to resolve disagreement in multi-annotator datasets.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Following this framework, we develop an algorithm for training an ensemble of models, each specialized for a different segment of the population.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 227. [Prompt Tuning as User Inherent Profile Inference Machine](https://openreview.net/forum?id=kAPiHV9Jo8)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=16
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Large Language Models (LLMs) have exhibited significant promise in recommender systems by empowering user profiles with their extensive world knowledge and superior reasoning capabilities.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large Language Models (LLMs) have exhibited significant promise in recommender systems by empowering user profiles with their extensive world knowledge and superior reasoning capabilities.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 228. [Similar Users-Augmented Interest Network](https://arxiv.org/abs/2604.23810v1)

- 发表时间/状态：2026-04-26；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Click-through rate (CTR) prediction is one of the core tasks in recommender systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：User behavior sequences, as one of the most effective features, can accurately reflect user preferences and significantly improve prediction accuracy.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 229. [Agentic AI for Education: A Unified Multi-Agent Framework for Personalized Learning and Institutional Intelligence](https://arxiv.org/abs/2604.16566v1)

- 发表时间/状态：2026-04-17；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Agentic Artificial Intelligence (AI) represents a paradigm shift from reactive systems to proactive, autonomous decision making frameworks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results demonstrate improvements in recommendation accuracy (92.4%), grading efficiency (94.1%), and dropout prediction (F1-score: 89.5%).
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 230. [CPGRec+: A Balance-oriented Framework for Personalized Video Game Recommendations](https://arxiv.org/abs/2604.14586v2)

- 发表时间/状态：2026-04-16；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：The rapid expansion of gaming industry requires advanced recommender systems tailored to its dynamic landscape.
- 数据集：Steam
- 主要结论：主要结论可从摘要中的结果句概括为：First, Preference-informed Edge Reweighting (PER) module assigns signed edge weights to qualitatively distinguish significant player interests and disinterests while then quantitatively measuring preference strength to mitigate over-smoothing in graph convolutions.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 231. [ProEx: A Unified Framework Leveraging Large Language Model with Profile Extrapolation for Recommendation](https://openreview.net/forum?id=7OhkQkOFoF)

- 发表时间/状态：2025-12-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：The powerful text understanding and generation capabilities of large language models (LLMs) have brought new vitality to general recommendation with implicit feedback.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The experimental results demonstrate that ProEx significantly enhances the performance of these base recommendation models.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 232. [A Survey on LLM-powered Agents for Recommender Systems](https://openreview.net/forum?id=umqji6Vzt3)

- 发表时间/状态：2025-02-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Recommender systems are essential components of many online platforms, yet traditional approaches still struggle with understanding complex user preferences and providing explainable recommendations.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This systematic examination not only illuminates the current state of LLM-powered agent recommender systems but also charts critical challenges and promising research directions in this transformative field.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 233. [Enhancing LLM-Based Recommendations Through Personalized Reasoning](https://openreview.net/forum?id=QPQFdKhrU7)

- 发表时间/状态：2025-02-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Due to the lack of explicit reasoning modeling, existing LLM-powered recommendations fail to leverage LLMs' reasoning capabilities effectively.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Due to the lack of explicit reasoning modeling, existing LLM-powered recommendations fail to leverage LLMs' reasoning capabilities effectively.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 234. [Personalization of Large Language Models: A Survey](https://openreview.net/forum?id=tf6A9EYMo6)

- 发表时间/状态：2024-12-01；Accepted by TMLR / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Personalization of Large Language Models (LLMs) has recently become increasingly important with a wide range of applications.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：By unifying and surveying recent research using the proposed taxonomies, we aim to provide a clear guide to the existing literature and different facets of personalization in LLMs, empowering both researchers and practitioners.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 235. [Graph Meets LLM for Review Personalization based on User Votes](https://openreview.net/forum?id=MHOhNKeJk8)

- 发表时间/状态：2024-10-07；WWW 2025 Poster / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Review personalization aims at presenting the most relevant reviews of a product according to the preferences of the individual user.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：It also indicates that our graph-LLM approach outperforms comparative baselines and algorithmic alternatives.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 236. [When large language models meet personalization: perspectives of challenges and opportunities](https://openreview.net/forum?id=JybbcaixWU)

- 发表时间/状态：2024-07-01；World Wide Web (WWW) 2024 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：The advent of large language models marks a revolutionary breakthrough in artificial intelligence.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：With the unprecedented scale of training and model parameters, the capability of large language models has been dramatically improved, leading to human-like performances in understanding, language synthesizing, common-sense reasoning, etc.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 237. [SmartAgent: Chain-of-User-Thought for Embodied Personalized Agent in Cyber World](https://openreview.net/forum?id=H5eBhe74Ib)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Recent advances in embodied agents with multimodal perception and reasoning capabilities based on large vision-language models (LVLMs), excel in autonomously interacting either real or cyber worlds, helping people make intelligent decisions in complex environments.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To demonstrate SmartAgent's capabilities, we also create a brand-new dataset SmartSpot that offers a full-stage personalized action-involved environment.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 238. [Visual Inception: Compromising Long-term Planning in Agentic Recommenders via Multimodal Memory Poisoning](https://arxiv.org/abs/2604.16966v1)

- 发表时间/状态：2026-04-18；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：The evolution from static ranking models to Agentic Recommender Systems (Agentic RecSys) empowers AI agents to maintain long-term user profiles and autonomously plan service tasks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on a mock e-commerce agent environment demonstrate that Visual Inception achieves about 85% Goal-Hit Rate (GHR), while CognitiveGuard reduces this risk to around 10% with configurable latency trade-offs (about 1.5s in lite mode to about 6.5s for full sequential verification), without quality degradation under our setup.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 239. [Response-Aware User Memory Selection for LLM Personalization](https://arxiv.org/abs/2604.14473v1)

- 发表时间/状态：2026-04-15；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：A common approach to personalization in large language models (LLMs) is to incorporate a subset of the user memory into the prompt at inference time to guide the model's generation.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We demonstrate that this information-theoretic foundation enables more principled user memory selection that aligns more closely with human selection compared to state-of-the-art methods, and models $400\times$ larger.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 240. [Learning in Blocks: A Multi Agent Debate Assisted Personalized Adaptive Learning Framework for Language Learning](https://arxiv.org/abs/2604.22770v1)

- 发表时间/状态：2026-03-29；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Most digital language learning curricula rely on discrete-item quizzes that test recall rather than applied conversational proficiency.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We introduce Learning in Blocks, a framework that grounds progression in demonstrated conversational competence evaluated using CEFR-aligned rubrics.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 241. [Bias can arise in memory Enhanced LLM Agents especially in Recruiting domain.](https://openreview.net/forum?id=ZEYRyQ5aTq)

- 发表时间/状态：2026-02-22；OpenReview / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：The authors propose the measurement of biases that may be induced in memory enhanced LLM agents due to inherent biases in the data and through their interpretations of this data as memory.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The paper also comes up with mitigation strategies primarily involving prompt augmentation that work well with agents using LLMs via API call and in situations where whitebox access to LLM internals is not feasible.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 242. [UCGRec: User-Centric Graph Learning for LLM-based Sequential Recommendation](https://openreview.net/forum?id=Jn5q6FuOfB)

- 发表时间/状态：2026-01-06；ACL ARR 2026 January Submission / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Recently, Large Language Models (LLM) have emerged as a promising paradigm for sequential recommendation.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：In sequential recommendation, effectively integrating diverse user preferences is essential for improving LLM performance, as users often exhibit multiple interests across different contexts.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 243. [InstructAgent: Building User Controllable Recommender via LLM Agent](https://openreview.net/forum?id=lqM4PyYuvo)

- 发表时间/状态：2025-02-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Traditional recommender systems usually take the user-platform paradigm, where users are directly exposed under the control of the platform's recommendation algorithms.
- 数据集：MIND
- 主要结论：主要结论可从摘要中的结果句概括为：To address these limitations, we propose a new user-agent-platform paradigm, where agent serves as the protective shield between user and recommender system that enables indirect exposure.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 244. [A global user profile framework for effective recommender systems](https://openreview.net/forum?id=3nHIXX31B9)

- 发表时间/状态：2024-05-01；Multim. Tools Appl. 2024 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Modern Recommender Systems (RSs) compete to maintain rich user profiles that can accurately reflect user behavior, interests, and service contexts.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：To keep up with the changes from the user perspective, an RS should maintain the making of effective personalization as supported by robust profile construction methods.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 245. [All Roads Lead to Rome: Unveiling the Trajectory of Recommender Systems Across the LLM Era](https://openreview.net/forum?id=hkwsaFwsO6)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Recommender systems (RS) are vital for managing information overload and delivering personalized content, responding to users' diverse information needs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Along these two paths, we point out that the information effectiveness of the recommendation is increased, while the user's acquisition cost is decreased.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 246. [LLM-Powered User Simulator for Recommender System](https://openreview.net/forum?id=G551r1464B)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：User simulators can rapidly generate a large volume of timely user behavior data, providing a testing platform for reinforcement learning-based recommender systems, thus accelerating their iteration and optimization.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, prevalent user simulators generally suffer from significant limitations, including the opacity of user preference modeling and the incapability of evaluating simulation accuracy.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 247. [Prospect Personalized Recommendation on Large Language Model-based Agent Platform](https://openreview.net/forum?id=Knhh4G5pqu)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：The new kind of Agent-oriented information system, exemplified by GPTs, urges us to inspect the information system infrastructure to support Agent-level information processing and to adapt to the characteristics of Large Language Model (LLM)-based Agents, such as interactivity.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：A preliminary study involving several cases of Rec4Agentverse validates its significant potential for application.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 248. [Filter bubbles and affective polarization in user-personalized large language model outputs](https://openreview.net/forum?id=3darGLCe5t)

- 发表时间/状态：2023-10-04；ICBINB 2023 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Echoing the history of search engines and social media content rankings, the advent of large language models (LLMs) has led to a push for increased personalization of model outputs to individual users.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This ``failure mode" should be monitored closely as there are more attempts to monetize and personalize these models.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 249. [Before You Interpret the Profile: Validity Scaling for LLM Metacognitive Self-Report](https://arxiv.org/abs/2604.17707v1)

- 发表时间/状态：2026-04-20；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Clinical personality assessment screens response validity before interpreting substantive scales.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Valid-profile models produce item-sensitive confidence (mean r = .18, 14 of 16 significant).
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 250. [Decisive: Guiding User Decisions with Optimal Preference Elicitation from Unstructured Documents](https://arxiv.org/abs/2604.18122v1)

- 发表时间/状态：2026-04-20；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Decision-making is a cognitively intensive task that requires synthesizing relevant information from multiple unstructured sources, weighing competing factors, and incorporating subjective user preferences.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Through extensive experiments, we demonstrate that our approach significantly outperforms both general-purpose LLMs and existing decision-making frameworks achieving up to 20% improvement in decision accuracy over strong baselines across domains.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 251. [ROZA Graphs: Self-Improving Near-Deterministic RAG through Evidence-Centric Feedback](https://arxiv.org/abs/2604.07595v3)

- 发表时间/状态：2026-04-08；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Language model agents reason from scratch on every query, discarding their chain of thought after each run.
- 数据集：HotpotQA
- 主要结论：主要结论可从摘要中的结果句概括为：(1) Dose-response: accuracy improves monotonically with evidence-profile coverage, reaching +10.6pp over Vanilla RAG at 50%+ coverage on the same questions (47% error reduction, $p<0.0001$; per-question Spearman $ρ=+0.144$, $p<10^{-6}$, $n=1{,}100$).
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 252. [Enhancing Cross-Domain Recommendations with Memory-Optimized LLM-Based User Agents](https://openreview.net/forum?id=vVLyl5yTeP)

- 发表时间/状态：2025-02-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：LLM-based user agents, which simulate user interaction behavior, are emerging as a promising approach to enhancing recommender systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：However, the memory design in current methods causes user agents to introduce significant irrelevant information during decision-making in cross-domain scenarios and makes them unable to recognize the influence of other users' interactions, such as popularity factors.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 253. [LLM-Rec: Personalized Recommendation via Prompting Large Language Models](https://openreview.net/forum?id=EUuSTpjmPF)

- 发表时间/状态：2024-01-21；OpenReview.net/Archive / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：We investigate various prompting strategies for enhancing personalized recommendation performance with large language models (LLMs) through input augmentation.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Our empirical experiments show that incorporating the augmented input text generated by LLM leads to improved recommendation performance.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 254. [A Hybrid User Profile Model for Personalized Recommender System with Linked Open Data](https://openreview.net/forum?id=Wk6C3nFUwz)

- 发表时间/状态：2014-01-01；ES 2014 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：In order to better enhance user experience on the web, varies applications such as search engines have integrated with recommender systems.
- 数据集：MovieLens
- 主要结论：主要结论可从摘要中的结果句概括为：The result shows Hy-UPMhas a better Mean Reciprocal Rank performance compared with other recommendation methods.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 255. [Context-aware search personalization with concept preference](https://openreview.net/forum?id=lgANt0Esrw)

- 发表时间/状态：2011-01-01；CIKM 2011 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：As the size of the web is growing rapidly, a well-recognized challenge for developing web search engines is to optimize the search result towards each user's preference.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results demonstrate that our approach captures accurate and comprehensive user's preference and, in terms of Top-N results quality, outperforms those existing concept-based personalization approaches without using search contexts.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 256. [Improving Social Filtering Techniques Through WordNet-Based User Profiles](https://openreview.net/forum?id=f22rO8yfb6)

- 发表时间/状态：2007-01-01；User Modeling 2007 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Collaborative filtering algorithms predict the preferences of a user for an item by weighting the contributions of similar users, called neighbors, for that item.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The results of an experimental session in a movie recommendation scenario demonstrate the effectiveness of the proposed approach.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 257. [TV Program Recommendation for Multiple Viewers Based on user Profile Merging](https://openreview.net/forum?id=jPOCzbJA7w)

- 发表时间/状态：2006-01-01；User Model. User Adapt. Interact. 2006 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Since today’s television can receive more and more programs, and televisions are often viewed by groups of people, such as a family or a student dormitory, this paper proposes a TV program recommendation strategy for multiple viewers based on user profile merging.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This paper first introduces three alternative strategies to achieve program recommendation for multiple television viewers, discusses, and analyzes their advantages and disadvantages respectively, and then chooses the strategy based on user profile merging as our solution.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 258. [Investigating the Effects of Different Levels of User Control in an Interactive Educational Recommender System](https://arxiv.org/abs/2605.01400v1)

- 发表时间/状态：2026-05-02；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。 摘要中的问题陈述是：Educational recommender systems (ERSs) are becoming increasingly important in enhancing educational outcomes and personalizing learning experiences by providing recommendations of personalized resources and activities to learners, tailored to their individual learning needs.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While user control is widely assumed to improve user experience, the effects of different levels of control in ERSs remain underexplored.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。


## Privacy, Federated, and On-device Personalization

这个方向处理个性化天然带来的隐私矛盾：越个性化越需要个人数据。近一年工作将联邦学习、本地小模型、隐私保护 adapter、去中心化偏好优化和日志最小化结合起来，目标是在不上传敏感历史的情况下获得用户级收益。它也是 OPPU 大规模部署必须面对的工程与伦理约束。

### 259. [Hierarchical Long-Term Semantic Memory for LinkedIn's Hiring Agent](https://arxiv.org/abs/2604.26197v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Large Language Model (LLM) agents are increasingly used in real-world products, where personalized and context-aware user interactions are essential.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive evaluations on LinkedIn's Hiring Assistant show that HLTM improves answer correctness and retrieval F1 significantly by more than 10%, while significantly advancing the Pareto frontier between query and indexing latency.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 260. [From Hidden Profiles to Governable Personalization: Recommender Systems in the Age of LLM Agents](https://arxiv.org/abs/2604.20065v1)

- 发表时间/状态：2026-04-22；arXiv / preprint
- 重要性与相关性：core；score=17
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Personalization has traditionally depended on platform-specific user models that are optimized for prediction but remain largely inaccessible to the people they describe.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We argue that the future of recommender systems will depend not only on better inference, but on building personalization systems that users can meaningfully understand, shape, and govern.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 261. [Federated User Behavior Modeling for Privacy-Preserving LLM Recommendation](https://arxiv.org/abs/2604.14833v1)

- 发表时间/状态：2026-04-16；arXiv / preprint
- 重要性与相关性：core；score=16
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Large Language Models have shown great success in recommender systems.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Large Language Models have shown great success in recommender systems.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 262. [ScrapMem: A Bio-inspired Framework for On-device Personalized Agent Memory via Optical Forgetting](https://arxiv.org/abs/2605.03804v1)

- 发表时间/状态：2026-05-05；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Long-term personalized memory for LLM agents is challenging on resource-limited edge devices due to high storage costs and multimodal complexity.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on the multimodal ATM-Bench showcase that ScrapMem provides three main benefits: (1) strong performance, achieving a new state-of-the-art with a 51.0% Joint@10 score; (2) high storage efficiency, reducing memory usage by up to 93% via optical forgetting; and (3) improved recall, increasing Recall@10 to 70.3% through structured aggregation.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 263. [HUOZIIME: An On-Device LLM-enhanced Input Method for Deep Personalization](https://arxiv.org/abs/2604.14159v1)

- 发表时间/状态：2026-03-23；arXiv / preprint
- 重要性与相关性：core；score=15
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Mobile input method editors (IMEs) are the primary interface for text input, yet they remain constrained to manual typing and struggle to produce personalized text.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Furthermore, we perform systemic optimizations tailored to on-device LLMbased IME deployment, ensuring efficient and responsive operation under mobile constraints.Experiments demonstrate efficient on-device execution and high-fidelity memory-driven personalization.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 264. [SecFPP : Secure Federated Prompt Personalization for Vision Language Models](https://openreview.net/forum?id=q2VKSHWhAS)

- 发表时间/状态：2025-09-20；ICLR 2026 Conference Withdrawn Submission / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Prompt learning has emerged as an effective and widely-adopted approach for customizing pre-trained vision language models (VLMs) to user-specific downstream tasks.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Prompt learning has emerged as an effective and widely-adopted approach for customizing pre-trained vision language models (VLMs) to user-specific downstream tasks.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 265. [Harmonizing Generalization and Personalization in Federated Prompt Learning](https://openreview.net/forum?id=YYwERRXsJW)

- 发表时间/状态：2024-01-22；ICML 2024 Poster / public_note
- 重要性与相关性：core；score=15
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Federated Prompt Learning (FPL) incorporates large pre-trained Vision-Language models (VLM) into federated learning through prompt tuning.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Addressing data heterogeneity in federated learning requires personalization, but excessive focus on it across clients could compromise the model's ability to generalize effectively.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 266. [CiPO: Counterfactual Unlearning for Large Reasoning Models through Iterative Preference Optimization](https://arxiv.org/abs/2604.15847v1)

- 发表时间/状态：2026-04-17；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Machine unlearning has gained increasing attention in recent years, as a promising technique to selectively remove unwanted privacy or copyrighted information from Large Language Models that are trained on a massive scale of human data.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：This iterative loop ensures both desirable unlearning and smooth optimization, effectively mitigating the dilemma.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 267. [Towards Personalizing Secure Programming Education with LLM-Injected Vulnerabilities](https://arxiv.org/abs/2604.13955v1)

- 发表时间/状态：2026-04-15；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：According to constructivist theory, students learn software security more effectively when examples are grounded in their own code.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：According to constructivist theory, students learn software security more effectively when examples are grounded in their own code.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 268. [Learning Evolving Preferences: A Federated Continual Framework for User-Centric Recommendation](https://arxiv.org/abs/2603.17315v1)

- 发表时间/状态：2026-03-18；arXiv / preprint
- 重要性与相关性：core；score=14
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：User-centric recommendation has become essential for delivering personalized services, as it enables systems to adapt to users' evolving behaviors while respecting their long-term preferences and privacy constraints.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments on four public benchmarks demonstrate the superior effectiveness of our approach, along with strong compatibility and practical applicability.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 269. [Automated Profile Inference with Language Model Agents](https://openreview.net/forum?id=IkGKEruteY)

- 发表时间/状态：2025-05-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Impressive progress has been made in automated problem-solving by the collaboration of large language models (LLMs) based agents.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experimental results on two real-world datasets and one synthetic dataset demonstrate that AutoProfiler is highly effective and efficient, and can be easily deployed on a web scale.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 270. [CheatAgent: Attacking LLM-Empowered Recommender Systems via LLM Agent](https://openreview.net/forum?id=TvMtoRiSIu)

- 发表时间/状态：2025-04-01；CoRR 2025 / public_note
- 重要性与相关性：core；score=14
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Recently, Large Language Model (LLM)-empowered recommender systems (RecSys) have brought significant advances in personalized user experience and have attracted considerable attention.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Recently, Large Language Model (LLM)-empowered recommender systems (RecSys) have brought significant advances in personalized user experience and have attracted considerable attention.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 271. [Replacing Parameters with Preferences: Federated Alignment of Heterogeneous Vision-Language Models](https://arxiv.org/abs/2605.03426v1)

- 发表时间/状态：2026-05-05；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Vision-Language Models (VLMs) have broad potential in privacy-sensitive domains such as healthcare and finance, yet strict data-sharing constraints render centralized training infeasible.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Experiments on diverse public vision-language benchmarks demonstrate that MoR consistently outperforms federated alignment baselines in generalization and cross-client adaptability.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 272. [Addressing the Reality Gap: A Three-Tension Framework for Agentic AI Adoption](https://arxiv.org/abs/2604.27245v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Generative AI has rapidly entered education through free consumer tools, outpacing the ability of schools and universities to respond.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We conclude the chapter with recommendations for educational leaders to proactively engage with the opportunities and challenges of AI, so that this technology can be harnessed to enhance teaching and learning in the decade ahead.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 273. [A Survey on the Security of Long-Term Memory in LLM Agents: Toward Mnemonic Sovereignty](https://arxiv.org/abs/2604.16548v1)

- 发表时间/状态：2026-04-17；arXiv / preprint
- 重要性与相关性：core；score=13
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Research on large language model (LLM) security is shifting from "will the model leak training data" to a more consequential question: can an agent with persistent, long-term memory be continuously shaped, cross-session poisoned, accessed without authorization, and propagated across shared organizational state?
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We unify these under mnemonic sovereignty -- verifiable, recoverable governance over what may be written, who may read, when updates are authorized, and which states may be forgotten -- arguing future secure agents will be differentiated not only by recall capacity, but by memory governance quality.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 274. [Fairness-guided federated training for generalization and personalization in cross-silo federated learning](https://openreview.net/forum?id=dxT1LuLXpc)

- 发表时间/状态：2025-01-01；Frontiers Inf. Technol. Electron. Eng. 2025 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Cross-silo federated learning (FL), which benefits from relatively abundant data and rich computing power, is drawing increasing focus due to the significant transformations that foundation models (FMs) are instigating in the artificial intelligence field.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Cross-silo federated learning (FL), which benefits from relatively abundant data and rich computing power, is drawing increasing focus due to the significant transformations that foundation models (FMs) are instigating in the artificial intelligence field.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 275. [Federated Recommendation with Additive Personalization](https://openreview.net/forum?id=xkXdE81mOK)

- 发表时间/状态：2023-09-21；ICLR 2024 poster / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Building recommendation systems via federated learning (FL) is a new emerging challenge for next-generation Internet service.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：We propose an effective curriculum to learn the local and global views progressively with increasing regularization weights.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 276. [Introduction to Emotions and Personality in Personalized Systems](https://openreview.net/forum?id=mwA7o9mKNL)

- 发表时间/状态：2017-01-01；Emotions and Personality in Personalized Services 2017 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Personalized systems traditionally used the traces of user interactions to learn the user model, which was used by sophisticated algorithms to choose the appropriate content for the user and the situation.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：The chapters cover (i) psychological theories, (ii) computational methods for the unobtrusive acquisition of emotions and personality, (iii) applications of personalized systems in recommender systems, conversational systems, music information retrieval, and e-learning, (iv) evaluation methods, and (v) privacy issues.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 277. [Privy: From Fine Print to Fair Practice in Privacy Rights Exercise](https://arxiv.org/abs/2605.02005v1)

- 发表时间/状态：2026-05-03；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Privacy regulations such as the CCPA and GDPR grant individuals rights over their personal data, yet it remains challenging for most users to exercise them in practice due to vague policy interpretation and unapproachable settings on web interfaces.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：A technical evaluation across 14 websites shows that Privy extracts rights with high precision (0.979) and completes 96.3\% of privacy tasks in an average of 3.2 steps.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 278. [FedKPer: Tackling Generalization and Personalization in Medical Federated Learning via Knowledge Personalization](https://arxiv.org/abs/2605.00698v1)

- 发表时间/状态：2026-05-01；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：Federated learning (FL) holds great potential for medical applications.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：While prior work has largely treated generalization and personalization as separate challenges, we show that a better balance between the two can be achieved through selective alignment with the global model and a modified aggregation scheme, which together mitigate the effects of statistical heterogeneity.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。

### 279. [DSIPA: Detecting LLM-Generated Texts via Sentiment-Invariant Patterns Divergence Analysis](https://arxiv.org/abs/2604.26328v1)

- 发表时间/状态：2026-04-29；arXiv / preprint
- 重要性与相关性：core；score=12
- 方法介绍：该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。 摘要中的问题陈述是：The rapid advancement of large language models (LLMs) presents new security challenges, particularly in detecting machine-generated text used for misinformation, impersonation, and content forgery.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Extensive experiments are conducted on state-of-the-art proprietary and open-source models, including GPT-5.2, Gemini-1.5-pro, Claude-3, and LLaMa-3.3.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。


## Domain Applications

这个方向把个性化 LLM 放进教育、健康、写作、代码、信息消费等具体场景。它们未必提出通用算法，但提供了真实需求：用户目标不同、专业背景不同、风险容忍度不同。近一年趋势是从演示式应用转向任务数据、长期行为和领域安全约束共建。

### 280. [Personalized Multimodal Large Language Models: A Survey](https://openreview.net/forum?id=gDtGLttgTL)

- 发表时间/状态：2024-01-01；CoRR 2024 / public_note
- 重要性与相关性：core；score=13
- 方法介绍：该工作把个性化 LLM 方法落到具体应用场景，重点是任务数据、用户差异和实际效益。 摘要中的问题陈述是：Multimodal Large Language Models (MLLMs) have become increasingly important due to their state-of-the-art performance and ability to integrate multiple data modalities, such as text, images, and audio, to perform complex tasks with high accuracy.
- 数据集：摘要未明确列出数据集；需正文核查
- 主要结论：主要结论可从摘要中的结果句概括为：Multimodal Large Language Models (MLLMs) have become increasingly important due to their state-of-the-art performance and ability to integrate multiple data modalities, such as text, images, and audio, to perform complex tasks with high accuracy.
- 与 LaMP/OPPU 的关系：属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。


## 附：可复现产物

- 路由 ledger：`D:\Codex_Sandbox\260527_Personalized\cache\director_flow\ledger.md`
- arXiv raw：`D:\Codex_Sandbox\260527_Personalized\cache\raw\arxiv_raw_records.jsonl`
- OpenReview raw：`D:\Codex_Sandbox\260527_Personalized\cache\raw\openreview_raw_records.jsonl`
- curated corpus：`D:\Codex_Sandbox\260527_Personalized\cache\processed\curated_papers.csv`
- verification：`D:\Codex_Sandbox\260527_Personalized\cache\reports\verification.md`
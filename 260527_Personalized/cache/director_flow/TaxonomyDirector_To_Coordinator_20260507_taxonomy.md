# Taxonomy report

- From: TaxonomyDirector
- To: Coordinator
- Subject: Taxonomy report
- Status: passed
- LoopType: FullLoop
- Supersedes: none
- RequiresAction: FinalWriter should use taxonomy.csv for section order and direction introductions.
- ArtifactLinks:
- D:\Codex_Sandbox\260527_Personalized\cache\processed\taxonomy.csv
- DoneCriteria: Built problem-driven taxonomy from curated corpus.

## Benchmark and Evaluation

这个方向回答“个性化 LLM 到底该如何评测”。LaMP 将用户历史转化为检索式 profile，并把 citation、tagging、rating、headline、title、email subject、tweet paraphrase 等任务统一为可比较的个性化生成/分类基准；近一年工作继续扩展到长历史、多轮记忆、更真实的用户行为和更细粒度的偏好差异。最新进展不是单纯提高分数，而是把评测从静态 profile 推向长期、动态、隐私受限和任务迁移环境。

Count: 65

## Profile Prompting and Personalized RAG

这个方向继承 LaMP 的检索式个性化思路：不改变模型参数，而是在推理时检索用户历史、画像、偏好证据或相似用户样本。发展脉络从简单拼接 profile，走向学习检索器、压缩长期历史、区分稳定偏好和临时意图，以及把 RAG 与记忆模块结合。最新工作更重视上下文预算、噪声 profile、冲突偏好和跨任务泛化。

Count: 13

## Personalized PEFT and Adaptation

这个方向以 OPPU 为中心：为每个用户或用户簇训练少量参数，让偏好沉淀在 adapter/LoRA/hypernetwork 中。它比 prompt 个性化更能吸收隐含行为模式，但面临用户规模、冷启动和更新成本问题。近一年论文重点在共享-私有参数分解、即时 adapter 生成、少样本用户数据、跨用户迁移和可扩展部署。

Count: 46

## Memory and Dynamic User Modeling

这个方向把个性化看作持续交互中的状态维护问题。早期 profile 多是离线静态文本，近一年工作更强调长期记忆写入、遗忘、冲突解决、时序偏好漂移和可解释调用。它与 agent 和 RAG 紧密相连：记忆既是检索库，也是决策状态。

Count: 6

## Personalized Alignment and Preference Learning

这个方向把用户差异推入对齐阶段，研究个体化 reward、DPO/RLHF、偏好聚合和多目标冲突。相较 OPPU 的任务适配，它更关心“不同用户认为好答案的标准不同”。最新进展集中在个体 reward 模型、联邦/私有偏好优化、跨域偏好泛化和避免过度迎合。

Count: 58

## Personalized Agents and Assistants

这个方向关注长期助手如何理解个人目标、工作流和工具偏好。与单次文本生成不同，agent 个性化需要在规划、调用工具、记忆更新和任务复盘中保持一致。最新工作通常把用户模型、记忆、反馈和环境状态合在一起，评估也更偏向真实任务完成度。

Count: 31

## LLM-based Recommendation and Ranking

这个方向是个性化 LLM 与推荐系统交汇处：LLM 被用来理解用户历史、生成解释、做 conversational recommendation，或作为排序/重排模型。发展脉络从把 LLM 当语义编码器，走向利用自然语言偏好、生成式用户模拟和多轮交互。最新进展关注冷启动、可解释性、长序列行为和推荐中的对齐风险。

Count: 39

## Privacy, Federated, and On-device Personalization

这个方向处理个性化天然带来的隐私矛盾：越个性化越需要个人数据。近一年工作将联邦学习、本地小模型、隐私保护 adapter、去中心化偏好优化和日志最小化结合起来，目标是在不上传敏感历史的情况下获得用户级收益。它也是 OPPU 大规模部署必须面对的工程与伦理约束。

Count: 21

## Domain Applications

这个方向把个性化 LLM 放进教育、健康、写作、代码、信息消费等具体场景。它们未必提出通用算法，但提供了真实需求：用户目标不同、专业背景不同、风险容忍度不同。近一年趋势是从演示式应用转向任务数据、长期行为和领域安全约束共建。

Count: 1

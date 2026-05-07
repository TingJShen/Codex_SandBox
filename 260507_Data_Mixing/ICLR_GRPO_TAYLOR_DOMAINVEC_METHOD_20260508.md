# ICLR Method Draft: Taylor-Guided GRPO Data Mixing with DomainVec Alignment

Date: 2026-05-08

This note records the current paper-level formulation of the V13-style method. It is written to address a key narrative issue found during discussion: the paper must not jump directly from a parameter-space Taylor expansion to DomainVec. The bridge is that domain mixing first rewrites the GRPO batch gradient as a weighted sum of domain-level expected gradients; DomainVec distance is then introduced only as an observable proxy for the otherwise expensive domain-level first-order alignment coefficient.

## Problem Definition

我们研究多领域数据上的大语言模型强化学习微调问题。给定训练语料

$$
\mathcal D=\bigcup_{i=1}^{K}\mathcal D_i,
$$

其中 $\mathcal D_i$ 表示第 $i$ 个训练领域，例如数学、代码或通用指令数据。每个样本记为 $x_n$，其领域标签为 $d_n\in\{1,\ldots,K\}$。在第 $t$ 步，策略模型为 $\pi_{\theta_t}$，参考模型为 $\pi_{\mathrm{ref}}$。

对于一个 prompt $x_n$，GRPO 从当前策略中采样一组回答

$$
\{y_{n,1},\ldots,y_{n,G}\}\sim \pi_{\theta_t}(\cdot|x_n),
$$

并通过奖励模型得到 reward $R_{n,k}$。GRPO 不依赖 value model，而是在同一组回答内部计算归一化优势：

$$
\hat A_{n,k}
=
\frac{
R_{n,k}-\mathrm{mean}_{j}(R_{n,j})
}{
\mathrm{std}_{j}(R_{n,j})+\epsilon
}.
$$

对应的单样本 GRPO 损失可写为：

$$
\ell_n^{\mathrm{GRPO}}(\theta)
=
-\frac{1}{G}
\sum_{k=1}^{G}
\min
\left(
\rho_{n,k}(\theta)\hat A_{n,k},
\mathrm{clip}(\rho_{n,k}(\theta),1-\epsilon,1+\epsilon)\hat A_{n,k}
\right)
+
\lambda_{\mathrm{KL}}
D_{\mathrm{KL}}
(\pi_{\theta}\|\pi_{\mathrm{ref}}),
$$

其中

$$
\rho_{n,k}(\theta)
=
\frac{
\pi_{\theta}(y_{n,k}|x_n)
}{
\pi_{\theta_t}(y_{n,k}|x_n)
}
$$

是策略比率，$\lambda_{\mathrm{KL}}$ 控制参考模型 KL 正则强度。于是样本 $x_n$ 诱导的 GRPO 梯度为：

$$
g_n
=
\nabla_{\theta}
\ell_n^{\mathrm{GRPO}}(\theta_t).
$$

若训练批次为 $B$，则实际更新方向为：

$$
g_B
=
\frac{1}{|B|}
\sum_{n\in B}g_n,
\qquad
\theta_{t+1}
=
\theta_t-\eta g_B,
$$

其中 $\eta$ 是学习率。

我们的目标是学习一个动态采样分布 $\mu_t(n)$，使得由 GRPO 产生的更新不仅提升当前训练 reward，也能更有效降低目标分布 $\mathcal T$ 上的风险：

$$
\mathcal L_{\mathcal T}(\theta)
=
\mathbb E_{x\sim \mathcal T}
[
\ell^{\mathrm{GRPO}}(x;\theta)
].
$$

这里 $\mathcal T$ 表示目标或验证 prompt 分布，仅用于构造分布锚点，不使用测试答案或测试 reward。我们将采样分布分解为领域级和样本级两部分：

$$
\mu_t(n)
=
p_t(d_n)\mu_t(n|d_n),
$$

其中 $p_t(d)$ 决定从哪个领域采样，$\mu_t(n|d)$ 决定在该领域内部选择哪些样本。

## Method

我们的核心思想是：把数据混合和样本选择统一为同一个 Taylor-guided GRPO sampling 问题。考虑一次 GRPO 更新对目标风险的影响，对 $\mathcal L_{\mathcal T}$ 在 $\theta_t$ 处做二阶展开：

$$
\mathcal{L}_{\mathcal{T}}(\theta_t-\eta g_B)
-
\mathcal{L}_{\mathcal{T}}(\theta_t)
\approx
-\eta
\nabla_\theta \mathcal{L}_{\mathcal{T}}(\theta_t)^\top g_B
+
\frac{\eta^2}{2}
g_B^\top H_{\mathcal{T}}(\theta_t)g_B,
$$

其中 $H_{\mathcal T}(\theta_t)=\nabla_\theta^2\mathcal L_{\mathcal T}(\theta_t)$ 是目标风险的 Hessian。第一项衡量当前批次梯度是否与目标风险下降方向一致，第二项衡量沿该方向更新可能带来的曲率代价。

为了把这个公式与领域混合联系起来，我们先定义领域 $i$ 的期望 GRPO 梯度：

$$
\bar g_i
=
\mathbb E_{x\sim \mathcal D_i}
[
\nabla_\theta
\ell^{\mathrm{GRPO}}(x;\theta_t)
].
$$

如果当前批次按照领域权重 $r=(r_1,\ldots,r_K)$ 采样，那么期望批次梯度可以近似写成：

$$
g_B(r)
\approx
\sum_{i=1}^{K}r_i\bar g_i.
$$

代入 Taylor 展开的一阶项，得到：

$$
-\eta
\nabla_\theta\mathcal L_{\mathcal T}(\theta_t)^\top g_B(r)
\approx
-\eta
\sum_{i=1}^{K}
r_i
\nabla_\theta\mathcal L_{\mathcal T}(\theta_t)^\top
\bar g_i.
$$

因此，领域级数据混合的本质是选择领域权重 $r_i$，使得被采样领域的平均 GRPO 梯度 $\bar g_i$ 尽可能与目标风险下降方向一致。然而，直接估计每个领域的完整梯度对齐项

$$
\nabla_\theta\mathcal L_{\mathcal T}(\theta_t)^\top \bar g_i
$$

代价很高，也不稳定。为此，我们引入 Distribution Alignment Assumption：训练混合分布越接近目标或验证分布，其目标风险越低。因此，领域分布与目标分布的距离可以作为领域级一阶梯度对齐的宏观代理。

具体而言，我们参考 DomainVec 思想，将每个训练领域压缩为一个领域向量：

$$
v_i
=
\mathrm{DomainVec}(\mathcal D_i),
$$

目标分布压缩为目标向量：

$$
v_{\mathcal T}
=
\mathrm{DomainVec}(\mathcal T).
$$

若目标分布包含多个 anchor，例如数学、代码和通用目标集合，则记为 $\{a_j\}_{j\in\mathcal G}$。领域 $i$ 的宏观分布偏移定义为：

$$
d_i
=
\sum_{j\in\mathcal G}
\mathrm{Dist}(v_i,a_j).
$$

这里 $d_i$ 衡量领域 $i$ 的整体分布与目标分布之间的距离。它不是样本难度，而是领域级一阶对齐代理：当 $d_i$ 较小时，表示该领域更接近目标分布，其平均 GRPO 梯度 $\bar g_i$ 更可能降低 $\mathcal L_{\mathcal T}$。

同时，我们引入领域训练动态项 $\mathrm{imp}_i$，用于描述领域 $i$ 最近 reward 的变化情况。它的作用是避免模型长期停留在某个语义上接近但收益已经停滞的领域。于是领域级代价定义为：

$$
c_i
=
\beta d_i+\gamma \mathrm{imp}_i,
$$

其中 $\beta$ 控制 DomainVec 分布对齐项的强度，$\gamma$ 控制 reward dynamics 项的强度。这个代价可以理解为 Taylor 一阶对齐项的可观测代理：

$$
\nabla_\theta\mathcal L_{\mathcal T}(\theta_t)^\top \bar g_i
\approx
-\beta d_i-\gamma \mathrm{imp}_i.
$$

因此，最小化 $c_i$ 等价于优先选择那些更接近目标分布、且仍具有训练收益的领域。

给定一个先验领域分布 $q$，我们通过 KL 正则化优化得到领域混合权重：

$$
p_t
=
\arg\min_{r\in\Delta_K}
\left[
\mathrm{KL}(r\|q)
+
\sum_{i=1}^{K}r_i
(\beta d_i+\gamma \mathrm{imp}_i)
\right].
$$

其中 $r_i$ 是领域 $i$ 的采样权重，$q_i$ 是先验分布，$\Delta_K$ 是 $K$ 维概率单纯形。该问题有闭式解：

$$
p_t(i)
=
\frac{
q_i\exp[-(\beta d_i+\gamma \mathrm{imp}_i)/\tau_D]
}{
\sum_{j=1}^{K}
q_j\exp[-(\beta d_j+\gamma \mathrm{imp}_j)/\tau_D]
},
$$

其中 $\tau_D$ 是领域级温度。这样，领域级数据混合就从 Taylor 一阶项自然推出：我们不是直接计算昂贵的领域梯度对齐，而是用 DomainVec 距离和 reward dynamics 构造其宏观代理。

在领域内部，我们进一步进行样本级控制。领域权重 $p_t(d)$ 只能决定“从哪个领域学”，但同一领域内不同样本对 GRPO 更新的贡献仍然不同。因此，我们对样本梯度进行低维投影：

$$
z_n
=
P g_n,
$$

其中 $P$ 是固定随机投影矩阵，$z_n$ 是样本 $n$ 的 GRPO gradient sketch。我们维护一个固定的 shadow anchor 集合 $A$，用于估计目标下降方向：

$$
\bar z_A
=
\frac{1}{|A|}
\sum_{a\in A}z_a.
$$

于是样本 $n$ 的一阶对齐收益近似为：

$$
\nabla_\theta\mathcal L_{\mathcal T}(\theta_t)^\top g_n
\approx
\bar z_A^\top z_n.
$$

为了刻画二阶曲率代价，我们用 anchor gradient sketch 的二阶矩构造低维 PSD 曲率代理矩阵：

$$
C_t
=
\mathrm{EMA}
\left(
\frac{1}{|A|}
\sum_{a\in A}
z_a z_a^\top
\right).
$$

这里 $C_t$ 可理解为目标 Hessian 在 sketch 空间中的 empirical-Fisher 或 Gauss-Newton 近似。于是样本 $n$ 的二阶代价近似为：

$$
g_n^\top H_{\mathcal T}(\theta_t)g_n
\approx
z_n^\top C_t z_n.
$$

根据 Taylor 展开，样本级采样应鼓励一阶对齐收益高、二阶曲率代价低的样本。因此，我们定义样本分数：

$$
s_t(n)
=
\lambda_{\mathrm{rel}}\mathrm{rel}_n
+
\lambda_{\mathrm{align}}
\bar z_A^\top z_n
-
\lambda_{\mathrm{curv}}
z_n^\top C_t z_n
+
\lambda_{\mathrm{learn}}\mathrm{learn}_n
+
\lambda_{\mathrm{age}}\mathrm{age}_n.
$$

其中 $\mathrm{rel}_n$ 表示 prompt 与目标 anchor 的语义相关性，$\bar z_A^\top z_n$ 表示样本 GRPO 梯度的一阶目标对齐收益，$z_n^\top C_t z_n$ 表示二阶曲率代价，$\mathrm{learn}_n$ 表示样本近期 reward EMA，$\mathrm{age}_n$ 表示样本多久没有被采样。对应的领域内采样概率为：

$$
\mu_t(n|i)
=
\frac{
\exp(s_t(n)/\tau_S)
}{
\sum_{m\in\mathcal C_i}
\exp(s_t(m)/\tau_S)
},
\qquad
n\in\mathcal C_i,
$$

其中 $\mathcal C_i$ 是领域 $i$ 当前候选窗口，$\tau_S$ 是样本级温度。

最终，完整采样分布为：

$$
\mu_t(n)
=
p_t(d_n)\mu_t(n|d_n).
$$

这个分解使宏观数据混合和微观样本选择对应同一个 Taylor 目标。领域级 $p_t(d)$ 使用 DomainVec 距离和 reward dynamics 近似 Taylor 一阶项中的领域平均梯度对齐；样本级 $\mu_t(n|d)$ 使用 GRPO gradient sketch 同时估计一阶对齐收益和二阶曲率代价。前者决定训练资源在不同领域之间如何分配，后者决定每个领域内部哪些样本更值得用于当前更新。二者共同构成一个从分布对齐到二阶样本控制的统一动态采样框架。

## Figure and Reader-Bridge Recommendation

### Main Readability Concern

对于完全不熟悉 RLHF、GRPO 或数据混合的读者，最容易卡住的地方不是某个单独公式，而是“为什么一个参数空间的 Taylor 展开会突然变成数据分布和 DomainVec”。因此主文需要增加一张桥接图，并在图前加入一小段直觉解释。核心目标是让审稿人在进入公式前先明白三件事：

1. GRPO 每一步本质上是由采样数据决定的梯度更新。
2. 数据混合改变的是期望 batch gradient 的方向。
3. DomainVec 不是替代梯度，而是领域平均梯度对齐项的可观测宏观代理。

### Recommended Figure

建议画一张三栏横向流程图，放在 Problem Definition 之后、Method 主要公式之前。

Panel A: GRPO update as target-risk change

- 左侧画当前策略模型 $\pi_{\theta_t}$。
- 从 prompt batch 产生多条 responses，经过 reward model 得到 group advantages。
- 得到 GRPO batch gradient $g_B$。
- 右侧显示目标风险变化：

$$
\Delta\mathcal L_{\mathcal T}
\approx
-\eta\nabla\mathcal L_{\mathcal T}^{\top}g_B
+
\frac{\eta^2}{2}g_B^\top H_{\mathcal T}g_B.
$$

这栏告诉读者：采什么数据，会改变 $g_B$，从而改变目标风险下降。

Panel B: macro domain mixing

- 画三个训练领域，例如 Math / Code / General。
- 每个领域压缩成一个 DomainVec $v_i$。
- 目标或验证 prompt 分布压缩成 target anchor $v_{\mathcal T}$ 或 $\{a_j\}$。
- 距离 $d_i=\mathrm{Dist}(v_i,v_{\mathcal T})$ 进入 KL-regularized mixer：

$$
p_t=\arg\min_{r\in\Delta_K}
\left[
\mathrm{KL}(r\|q)+\sum_i r_i(\beta d_i+\gamma\mathrm{imp}_i)
\right].
$$

输出领域预算 $p_t(d)$。

这栏告诉读者：领域混合是在控制期望 batch gradient 的宏观方向。

Panel C: micro sample selection

- 在某个领域内部画候选样本窗口 $\mathcal C_i$。
- 每个样本产生 gradient sketch $z_n=P g_n$。
- shadow anchor 产生平均方向 $\bar z_A$ 和曲率代理 $C_t$。
- 样本分数包含：

$$
\bar z_A^\top z_n
\quad\text{and}\quad
z_n^\top C_t z_n.
$$

- 输出领域内采样分布 $\mu_t(n|d)$。
- 最终合并为：

$$
\mu_t(n)=p_t(d_n)\mu_t(n|d_n).
$$

这栏告诉读者：样本选择是在领域预算内进一步选择“一阶对齐高、二阶代价低”的样本。

### Suggested Caption

Figure X: Overview of Taylor-guided GRPO data mixing. A GRPO update changes the target risk through a first-order alignment term and a second-order curvature term. At the macro level, we decompose the expected batch gradient into domain-level expected GRPO gradients and use DomainVec distance as an observable proxy for domain-level first-order alignment under the Distribution Alignment Assumption. At the micro level, we score candidate samples using low-dimensional GRPO gradient sketches, encouraging samples aligned with the anchor direction while penalizing high-curvature updates. The final sampling distribution factorizes as $\mu_t(n)=p_t(d_n)\mu_t(n|d_n)$.

### Suggested Intuition Paragraph Before Method

建议在 Method 的第一个公式前加入下面这段短说明：

在强化学习微调中，数据采样并不是一个独立于优化的预处理步骤。每个采样到的 prompt 都会通过 GRPO 产生一组 responses、advantages 和一个策略梯度，因此“选择哪些数据”本质上是在选择下一步参数更新的方向。我们的目标是选择那些更可能降低目标分布风险的训练样本。为此，我们先在领域级控制 batch gradient 的平均方向：若某个领域的 DomainVec 更接近目标分布，根据 Distribution Alignment Assumption，它更可能产生对目标风险有利的平均更新。随后，我们在领域内部进一步比较样本级 gradient sketch，优先采样一阶对齐更强且二阶曲率代价更低的样本。

### Why This Figure Matches ICLR Expectations

这张图比单纯画算法流程更适合 ICLR，因为它明确回答了审稿人可能提出的三个理论问题：

1. 为什么数据混合可以和优化目标相关：因为领域权重改变 $g_B(r)=\sum_i r_i\bar g_i$。
2. 为什么 DomainVec 合理：它只作为不可观测梯度对齐系数的宏观代理，而不是替代 Taylor 展开。
3. 为什么样本级控制有二阶意义：因为 $z_n^\top C_t z_n$ 是 $g_n^\top H_{\mathcal T}g_n$ 在低维 sketch 空间的 PSD 代理。

建议主图保持极简，把完整推导放在 Method；图中只保留三条主线：GRPO update, DomainVec macro mixing, gradient-sketch micro selection。这样非本领域读者可以先理解“数据选择改变梯度，梯度改变目标风险”，再进入具体公式。

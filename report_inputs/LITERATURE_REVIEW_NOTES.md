# Verified literature review notes for the five assigned sources

## Review policy and source status

The identities below were cross-checked against the supplied execution guide and the reference list in the supplied Nigam PDF, then checked against publisher or author/repository records. Three works have full-text PDFs in the package: Jullien, the Wadhawan arXiv version, and the supplied Nigam copy. Pilarski and Li full texts are publicly accessible at the linked records, but source-host restrictions prevented saving their PDFs into this ZIP. This distinction is not a claim that their works are absent online.

The assignment and guide ask for comparison of these five sources. Do not claim that a method is absent from an article unless its full text was checked. Do not use the Nigam paper's bibliography as independently validated evidence: it has a duplicate/inconsistent Pilarski entry, and the provided copy's publication status could not be verified.

## 1. Pilarski, Sidhu, and Varró (2025)

**Identity.** Sebastian Pilarski, Aman Sidhu, and Dániel Varró, “Combining simulation and reinforcement learning to reduce food waste in food retail,” *Simulation*, vol. 101, no. 3, pp. 267–285, issue March 2025; first published online December 30, 2024. DOI: [10.1177/00375497241299054](https://doi.org/10.1177/00375497241299054). The publisher identifies the article as open access under CC BY 4.0. The final full text is hosted by [Linköping University DiVA](https://liu.diva-portal.org/smash/get/diva2:1928671/FULLTEXT01.pdf) and at the [SAGE article record](https://journals.sagepub.com/doi/abs/10.1177/00375497241299054). The PDF was not locally retrievable from this environment.

**Objective and method.** The paper develops a discrete-event food-retail simulator with wholesaler, store, and customer interactions so reinforcement-learning policies can control ordering and prices. It synthesizes daily demand from historical consumption/price statistics and evaluates PPO, SAC, and DQN with alternative reward formulations for strawberries, potatoes, and carrots. The paper evaluates 1,000 simulated trajectories over an unseen three-year test period and compares against two baselines.

**Reported findings.** Relative to a baseline representing typical retail waste, the authors report 78–92% average food-waste reductions; the best RL policy reports profit improvement up to 12.3% over another baseline. The article also reports algorithm/reward stability variation and does not claim one configuration is best for every product.

**Limitations and relevance.** It is a computational inventory-policy study, not a colorimetric shelf-label study. Its state/action focus is product ordering and price; it does not establish the accuracy of virtual printed colors or the effect of label misclassification on donation triggers. It is relevant as a simulation-based retail waste baseline. It supports using reproducible simulation but does not validate this project's observer assumptions.

**Novelty comparison boundary.** The defensible distinction is that this Q3 implementation connects color-science calculations and an explicitly assumed recognition model to a separate illustrative donation-capacity model. Do not say Pilarski does not consider a feature without checking the full paper; the article's main described contribution is retail simulation and RL policy assessment.

## 2. Jullien et al. (2023)

**Identity.** Sami Jullien, Mozhdeh Ariannezhad, Paul Groth, and Maarten de Rijke, “A Simulation Environment and Reinforcement Learning Method for Waste Reduction,” *Transactions on Machine Learning Research* (04/2023), Article 769. The source record is [OpenReview forum KSvr8A62MD](https://openreview.net/forum?id=KSvr8A62MD); arXiv preprint: [arXiv:2205.15455](https://arxiv.org/abs/2205.15455). The final published PDF is included as `03_REFERENCE_PAPERS/Jullien/Jullien_2023_TMLR.pdf`; UvA-DARE metadata identifies it as the final published version under CC BY.

**Objective and method.** The paper frames replenishment of perishable grocery inventory as a stochastic, partially observed RL task. It introduces RetaiL, built from retailer data and expert knowledge, and GTDQN, which models the reward distribution with a generalized Tukey Lambda distribution. Its method studies uncertainty in demand and waste outcomes rather than relying only on a mean reward estimate. Code and model details are linked by the paper.

**Reported findings.** The authors report GTDQN as a strong baseline that outperforms other distributional-RL approaches in overall reward and generated waste in the tested partially observable setting. The paper's result is specific to its benchmark and configuration and should not be transferred numerically to Q3's different donation/colour model.

**Limitations and relevance.** The paper notes limitations including the discrete action-space formulation and dependence on simulated/permitted item generation. It is relevant to transparent synthetic retail modeling and stochastic outcomes. It does not evaluate D65, LED spectra, printed labels, CIEDE2000, or human recognition of expiry-warning colors.

## 3. Li, Chiu, and Seva (2023)

**Identity.** Richard Li, Anthony S. F. Chiu, and Rosemary Seva, “Reducing carbon footprint and promoting resource sustainability in the retail industry through the prevention of dead stocks,” *Cleaner and Responsible Consumption*, vol. 11, article 100150, 2023. DOI: [10.1016/j.clrc.2023.100150](https://doi.org/10.1016/j.clrc.2023.100150). The full-text record identifies CC BY-NC-ND 4.0. The [publisher record](https://www.sciencedirect.com/science/article/pii/S2666784323000517) and an [author-uploaded full-text record](https://www.researchgate.net/publication/375102523_Reducing_carbon_footprint_and_promoting_resource_sustainability_in_the_retail_industry_through_the_prevention_of_dead_stocks) were verified. Publisher PDF retrieval from this workspace returned HTTP 403, so the binary is not included.

**Objective and method.** The article proposes an inventory-classification approach that includes remaining shelf life alongside business-performance indicators to identify potential dead stock and dead stock. The study uses retail datasets from open databases, decision rules, one-way ANOVA to assess classification consistency, and Monte Carlo simulation to estimate multi-period transitions.

**Reported findings.** The authors report that 17% of potential dead stock, if undetected, becomes dead stock in the following period, and that their modeled reduction in disposal prevents more than one ton of carbon emissions. These are the paper's reported outcomes, not results of the Q3 project. The article states that the underlying data are confidential.

**Limitations and relevance.** This work addresses inventory classification and shelf-life-based prioritization rather than display-color fidelity or color-dependent recognition. It is relevant to the transition from near-expiry risk to dead stock and motivates the retail context. Because its data are confidential and the PDF is not locally bundled, Claude should cite publisher metadata and the available full text online, not claim independent re-analysis.

## 4. Wadhawan and Rizvi (2024 preprint; 2025 journal article)

**Identity.** I. B. Wadhawan and M. M. Rizvi, “Optimizing inventory management through multiobjective reverse logistics with environmental impact.” The bundled full text is the CC BY 4.0 arXiv preprint [arXiv:2406.13226v1](https://arxiv.org/abs/2406.13226), dated June 2024, at `03_REFERENCE_PAPERS/Wadhawan/Wadhawan_Rizvi_2024_arXiv.pdf`. The final article is *Applied Mathematical Modelling*, vol. 146, article 116166 (2025), DOI [10.1016/j.apm.2025.116166](https://doi.org/10.1016/j.apm.2025.116166). Do not confuse the 2024 preprint year with the final 2025 publication year.

**Objective and method.** The work develops mixed-integer inventory models for reverse logistics with new and repaired/remanufactured products. It incorporates environmental waste/disposal objectives, solution procedures, scalarization methods for Pareto solutions, numerical experiments, and sensitivity analysis.

**Reported findings.** The authors report that the optimization formulations and solution procedures are checked through numerical experiments and that scalarization approaches approximate trade-offs between inventory cost and waste/environmental objectives. Any numerical result quoted in the paper must be taken from the exact cited version and clearly attributed to that model.

**Limitations and relevance.** The modeled domain is reverse logistics and repaired-product inventory, not near-expiry food donation or shelf-label perception. It broadens the environmental inventory context but does not validate this project's sustainability factor or donation capacity. The local copy is the preprint; the published citation is provided separately.

## 5. Nigam et al. (supplied course copy; publication status unverified)

**Identity and source status.** Meghna Nigam, Lithu Mathew, Rahul Maity, and Anju Pathrose, “RL-Driven Retail Waste Management: A Multi-Objective Optimization Framework for Sustainable Inventory Control and Carbon Reduction.” The supplied five-page PDF is included as `03_REFERENCE_PAPERS/Nigam/Nigam_Assigned_Copy_retail_waste_managment_RL.pdf`. No venue, DOI, or publication date is visible in the supplied copy; exact-title searches did not establish an independent publisher record. Treat it as supplied course material unless the instructor provides a definitive citation.

**Objective and method described by the supplied copy.** It describes a five-category retail-waste environment, a tabular Q-learning agent with epsilon-greedy exploration and experience replay, moving-average demand prediction, eight action types (restock, three discounts, donate, and three waste-removal choices), and five named scenarios: High Demand, Near Expiry, Overstocked, Expired Products, and Low Stock. It gives a multi-objective reward and a sustainability-score expression. The guide's suggestions to adopt Nigam's exact parameters/formula are therefore source instructions, not implemented project facts.

**Reported results and internal consistency.** The copy reports over 3,500 training episodes, average profit of $6.48, a carbon-footprint value of 0.50 kg CO₂, sustainability score 1.00, and no waste in a stated final episode. Its test table reports Near-Expiry 0/11 passes, High-Demand 1/11 (9.1%), Overstocked 2/11 (18.2%), Expired Products 8/11 (72.7%), and Low Stock 0/11. The text separately says Near-Expiry sustainability remained below 0.9. It labels a final product-status figure as Episode 499 despite the 3,500-episode claim. The reference list duplicates the Pilarski title with conflicting authors/page numbers: reference [14] matches the independently verified Pilarski paper and DOI, while [1] does not match that record. These inconsistencies mean the numbers should be quoted only as claims made by the supplied document, not independently reproduced facts.

**Limitations and relevance.** The copy is useful as the assignment's near-expiry/donation-capacity motivation, but its numeric donation capacity is not clearly specified in the retrieved methods, and its event/cost/carbon coefficients are not given external provenance. The Q3 inventory and sustainability models remain alternative, explicitly labeled simulations. No Nigam equations, scores, or reported values are presented as outputs of this project.

## Cross-paper comparison and defensible gap

These works cover retail simulation and reinforcement learning, shelf-life-based dead-stock classification, and environmental/reverse-logistics inventory optimization. The Q3 software adds a narrowly scoped computational linkage from colorimetric difference under three modeled illuminants to an assumed observer-confusion process and then to an alternative donation-capacity simulation. This is a model integration, not a demonstrated real-world behavioral effect. No source here supplies empirical evidence that the project's modeled ΔE00 predicts actual store-worker donation decisions. The eventual paper must keep this boundary explicit and avoid a “first” claim unless a systematic review supports it.

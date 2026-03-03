# Group F
# Feasibility Study

---

## Gesture Recognition

**Challenges**
- Hard to achieve stable hand recognition — lighting and brightness heavily impact accuracy
- Unintended movements (e.g. adjusting hair) can trigger false inputs

**Mitigation**
- Implement a confirmation gesture to validate the player's choice
- Define a delimited bounding square where all valid movements must occur

*Verdict: Doable with proper constraints in place.*

---

## UniScratch

**Strengths**
- No hardware needed
- Backend complexity stays low if block commands remain simple
- Largest effort lies in front-end development
- Immerses users in computer science, offering a tangible glimpse into programming logic

*Verdict: Highly feasible; front-end is the main workload.*

---

## Fruit Ninja

**Challenges**
- Same hand-movement and lighting issues as Gesture Recognition
- Movements must be fast, amplifying detection difficulty

**Appeal**
- High interactivity makes it attractive to a broad audience

*Verdict: Technically riskier due to speed requirements; strong engagement potential.*

---

## Data Analytics Quiz

**Strengths**
- No hardware, low complexity
- Easily adaptable across different screen sizes

**Weakness**
- Lower appeal for the general public compared to interactive alternatives

*Verdict: Easiest to implement; limited wow-factor.*

---

## Rock Paper Scissors

**Challenges**
- Camera-based detection still poses difficulties
- Mitigated by only needing 3 distinct hand gestures — more manageable than other gesture projects

**Strengths**
- Rich documentation on RPS probabilities makes it easy to train a predictive bot for Hard Mode
- Easy Mode uses a random bot — trivial to implement
- Showcases multiple CS concepts (ML, probability, game logic) in a single project

*Verdict: Strong candidate — manageable scope with high educational and interactive value.*

---

## Comparison

| Project             | Complexity | Appeal | Feasibility |
|---------------------|------------|--------|-------------|
| Gesture Recognition | Medium     | Mid    | Moderate    |
| UniScratch          | Medium     | High   | High        |
| Fruit Ninja         | High       | High   | Moderate    |
| Data Analytics Quiz | Low        | Low    | High        |
| Rock Paper Scissors | Medium     | High   | High        |

# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student reviews of CS professors at City Colleges of Chicago — Wright College, collected from Rate My Professors. This knowledge is valuable because official course descriptions reveal nothing about teaching style, exam difficulty, workload, or professor personality. The only way to access this information through Rate My Professors is to search for each professor individually, which is tedious when there are nearly 20 professors teaching dozens of classes. There is no official, central collection of this data.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — Abdul Khan | .txt | documents/Abdul_Khan.txt |
| 2 | Rate My Professors — Dan Grigoletti | .txt | documents/Dan_Grigoletti.txt |
| 3 | Rate My Professors — Douglas Kaniuk | .txt | documents/Douglas_Kaniuk.txt |
| 4 | Rate My Professors — Duke Best | .txt | documents/Duke_Best.txt |
| 5 | Rate My Professors — Erika Nadas | .txt | documents/Erika_Nadas.txt |
| 6 | Rate My Professors — Gustavo Alatta | .txt | documents/Gustavo_Alatta.txt |
| 7 | Rate My Professors — Laurie Alfaro | .txt | documents/Laurie_Alfaro.txt |
| 8 | Rate My Professors — Luke Papademas | .txt | documents/Luke_Papademas.txt |
| 9 | Rate My Professors — Mohammed Hossain | .txt | documents/Mohammed_Hossain.txt |
| 10 | Rate My Professors — Ogar Haji | .txt | documents/Ogar_Haji.txt |

---

## Chunking Strategy

**Chunk size:** Variable — each chunk is one complete review block, defined as all text between consecutive `\n\n` delimiters. Individual reviews range from roughly 80 to 400 characters depending on how much the student wrote.

**Overlap:** 0. Any overlap at review boundaries would introduce text from a different student's review into the adjacent chunk, conflating two separate opinions into one retrieval unit.

**Why these choices fit your documents:** Reviews are naturally self-contained paragraphs — every `\n\n` in the source files marks the exact boundary between one student's opinion and the next. A fixed character or token size would either split a single review across two chunks (losing the context of a complete thought) or merge multiple reviews into one chunk (mixing sentiments from different students about different aspects of the course). Splitting on `\n\n` aligns chunking with the document's own semantic boundaries without any arbitrary size decision. The professor's name is prepended to every chunk as `"Professor: {Name}\n"` so that name-based queries can match the correct reviews at retrieval time.

**Final chunk count:** 91 chunks across 10 documents (run `python ingest.py` to reproduce).

---

## Sample Chunks

Each chunk below is shown exactly as stored, with the professor name prepended and the source file labeled.

---

**Chunk 1 — Source: Abdul_Khan.txt**
```
Professor: Abdul Khan
Quality
3.0
Difficulty
1.0
Class: CIS142
Feb 1st, 2024
For Credit: Yes
Attendance: Not Mandatory
Grade: A
Textbook: Yes
Online Class: Yes
Often make mistakes during presentations but it doesn't matter because the material is copied and pasted and I learned more on my own than in this class.
```

---

**Chunk 2 — Source: Abdul_Khan.txt**
```
Professor: Abdul Khan
Quality
4.0
Difficulty
3.0
Class: CIS242
Jun 23rd, 2019
For Credit: Yes
Attendance: Not Mandatory
Would Take Again: Yes
Grade: A
Textbook: Yes
In this CIS 242 with Dr. Khan (Fall 2018), I learned so much more C++ material that I didn't learn in my CIS 142, although there can be a bit of overlap at the start that you'll have to get by. Grade is 30% homework/lab coding assignments (6 of each), 10% quizzes, 30% midterm exam, 30% final exam. Class was hybrid so we met every other week.
Get ready to read Test heavy Clear grading criteria
```

---

**Chunk 3 — Source: Duke_Best.txt**
```
Professor: Duke Best
Quality
5.0
Difficulty
2.0
Class: CIS101
Oct 13th, 2025
Attendance: Mandatory
Would Take Again: Yes
Grade: A+
Textbook: N/A
Online Class: Yes
Professor was highly devoted to helping us understand concepts and real life application. We had great speakers in the industry that provided career path feedback. I appreciated the help on topics and his professionalism.
Inspirational Hilarious Accessible outside class
```

---

**Chunk 4 — Source: Duke_Best.txt**
```
Professor: Duke Best
Quality
5.0
Difficulty
3.0
Class: CIS101
Jan 25th, 2024
For Credit: Yes
Attendance: Mandatory
Would Take Again: Yes
Grade: A+
Textbook: Yes
Online Class: Yes
Duke is a great professor. He is very passionate about his work and he's willing to help you whenever you need it!
```

---

**Chunk 5 — Source: Duke_Best.txt**
```
Professor: Duke Best
Quality
5.0
Difficulty
1.0
Class: CIS101
Feb 18th, 2025
Attendance: Not Mandatory
Would Take Again: Yes
Grade: A+
Textbook: N/A
Online Class: Yes
He was always made himself available to meet during his office hours. He has a lot industry experience and has shared valuable insights relevant to the field. He is very helpful in providing direction and guidance not only in the course but also real world applications in field. I would take his course again.
Amazing lectures Caring Accessible outside class
```

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

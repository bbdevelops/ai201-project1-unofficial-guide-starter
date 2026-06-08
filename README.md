# The Unofficial Guide — Project 1

Demo Video: https://vimeo.com/1199288880
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

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. This model encodes text into 384-dimensional vectors and was selected because it is fast, runs locally without an API key, and is well-suited for short-to-medium English text like student reviews. ChromaDB stores and searches the vectors using cosine distance (lower score = more similar).

**Production tradeoff reflection:** One consideration would be the use of slang in the reviews. The lightweight `all-MiniLM-L6-v2` model might miss the semantic meaning of informal language, abbreviations, or misspellings common in student reviews, leading to less accurate embeddings. A larger, more sophisticated proprietary model like OpenAI's `text-embedding-3-large` might better capture this informal register. Another issue is throughput under load: if usage spikes near registration deadlines, a locally-run model may not scale fast enough, making a commercial embedding API a better option. For a fully offline, privacy-respecting deployment with no cost ceiling, the inference infrastructure could be hosted locally using a larger model such as `bge-large-en-v1.5` or a domain-fine-tuned variant.

---

## Retrieval Test Examples

For each query below, the top 5 chunks returned by `retrieve_context()` are shown with their source file and cosine distance score (0 = identical, lower = more relevant). Tests were run after building the vector store with all 91 chunks.

---

### Query 1: How does Professor Best connect his coursework to the real world and the tech industry?

| Rank | Source | Distance |
|------|--------|----------|
| 1 | Duke_Best.txt | 0.4147 |
| 2 | Duke_Best.txt | 0.4206 |
| 3 | Duke_Best.txt | 0.4362 |
| 4 | Duke_Best.txt | 0.4479 |
| 5 | Dan_Grigoletti.txt | 0.4909 |

**Top returned chunk (Rank 1):**
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

**Rank 3 chunk (most directly answers the question):**
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

**Why these chunks are relevant:** The query asks specifically about real-world application and the tech industry. Ranks 1 and 3 are the two most directly relevant chunks: Rank 1 mentions "industry experience" and "real world applications in field," and Rank 3 explicitly mentions "great speakers in the industry that provided career path feedback." Both are from `Duke_Best.txt`, confirming that retrieval correctly focused on the right professor. The Rank 5 result (Dan Grigoletti) is a near-miss — it mentions teaching in multiple locations and being "very knowledgeable," which shares some semantic overlap with "real-world experience" language even though it isn't about Professor Best.

---

### Query 2: What should a student expect regarding the workload, homework, and exams in Professor Khan's classes?

| Rank | Source | Distance |
|------|--------|----------|
| 1 | Abdul_Khan.txt | 0.2796 |
| 2 | Abdul_Khan.txt | 0.3427 |
| 3 | Abdul_Khan.txt | 0.3529 |
| 4 | Abdul_Khan.txt | 0.3598 |
| 5 | Abdul_Khan.txt | 0.3636 |

**Top returned chunk (Rank 1):**
```
Professor: Abdul Khan
Quality
1.5
Difficulty
2.0
Class: CIS120
Nov 9th, 2015
For Credit: Yes
Attendance: Mandatory
Grade: A
Textbook: Yes
Lectures are long. Has accent. Sometimes gets confused. For me the class is easy because I have a source of all the quizzes and exams. Overall. Assignments online are easy. There is no way you cant get a 100. quizzes and exams are hard. You will need the book.
```

**Rank 4 chunk:**
```
Professor: Abdul Khan
Quality
1.0
Difficulty
5.0
Class: CIS142
Nov 10th, 2013
Attendance: Mandatory
Grade: A+
Textbook: No
Strong accent. 2hr lectures(where will just keep on talking about the powerpoint NONESTOP) he is a little outdated on C# cause he cant even explain certain things to us when we ask him. 2hr lab where he makes you do a program. He has 2 exams midterm and finals, so do good on it. He gives weekly assignments. He doesnt email. Late on grading too!
```

**Why these chunks are relevant:** The query targets workload, homework, and exams — all highly specific terms. All 5 returned chunks are from `Abdul_Khan.txt`, and the distances (0.28–0.36) are the lowest of any query in this test, indicating strong semantic alignment. Rank 1 mentions "quizzes and exams" and "Assignments online," directly matching the query vocabulary. Rank 4 explicitly describes "2 exams midterm and finals" and "weekly assignments," which corresponds closely to the expected answer in the evaluation plan. The fact that all 5 results are from the same source file confirms that the professor-name prepending strategy is working — the name "Abdul Khan" in the query aligns with the `"Professor: Abdul Khan"` prefix in every chunk from that file.

---

### Query 3: What do students say about the textbook used in Professor Haji's class?

| Rank | Source | Distance |
|------|--------|----------|
| 1 | Ogar_Haji.txt | 0.2403 |
| 2 | Ogar_Haji.txt | 0.3349 |
| 3 | Ogar_Haji.txt | 0.3564 |
| 4 | Ogar_Haji.txt | 0.3725 |
| 5 | Ogar_Haji.txt | 0.4008 |

**Top returned chunk (Rank 1):**
```
Professor: Ogar Haji
Quality
1.0
Difficulty
3.0
Class: CIS144
Jan 30th, 2024
For Credit: Yes
Attendance: Mandatory
Grade: Drop/Withdrawal
Textbook: N/A
Online Class: Yes
Professor uses his own self written "textbook", which is ridden with grammar errors and poor English, multiple horrible contrasting colors, different sized fonts, and highlighted words which makes it very hard to read (not to mention the excessive clipart). Knowing I'm going to strain my eyes with this "textbook" makes me feel discouraged.
Get ready to read Participation matters Lecture heavy
```

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt is the primary enforcement mechanism. It is passed as the `system` role message so it cannot be overridden by the user message. The exact instruction:

```
You are a helpful assistant answering questions about CS professors at Wright College
based exclusively on student reviews provided to you.

Rules you must follow:
1. Answer ONLY from the review excerpts in the context below. Do not use your general
   training knowledge about teaching, universities, or any topic.
2. If the provided reviews do not contain enough information to answer the question,
   respond with exactly: "I don't have enough information in the provided reviews to
   answer that question."
3. At the end of every response, list the source files you drew from, formatted as:
   Sources: [filename1.txt, filename2.txt]
4. When multiple reviews say different things, summarize the range of opinions fairly.
```

**How source attribution is surfaced in the response:**

The five retrieved chunks are injected into the user message, each prefixed with `[Source: filename.txt]`. This gives the LLM the filenames directly in the evidence it reads, so it can follow Rule 3 and cite them accurately at the end of its response. The Gradio interface also surfaces a separate "Retrieved from" field populated from the retrieval metadata, independent of what the LLM writes.

**Example response 1 — in-scope query with source attribution:**

> **Question:** How does Professor Best connect his coursework to the real world and the tech industry?
>
> **System response:**
> Professor Best connects his coursework to the real world and the tech industry by sharing valuable insights relevant to the field, providing direction and guidance on real-world applications, and inviting great speakers from the industry to provide career path feedback. He also encourages students to expand their learning outside of textbooks, which helps them understand the practical applications of the concepts learned in class.
>
> Sources: Duke_Best.txt

**Example response 2 — in-scope query with source attribution:**

> **Question:** What do students say about the textbook used in Professor Haji's class?
>
> **System response:**
> Students have varying opinions about the textbook used in Professor Haji's class. One student mentioned that in the CIS144 class, Professor Haji uses his own self-written "textbook" which is ridden with grammar errors, poor English, and has a visually unappealing format, making it hard to read. In another review for CIS120S, the student stated that the lectures are based on the book, but did not comment on the book's quality. In the CIS120 class, one student mentioned that there is no textbook. However, in a different review for CIS144, the student stated that there is a textbook and suggested that if students don't understand the concepts from it, they can look it up online.
>
> Sources: Ogar_Haji.txt

**Out-of-scope query example — refusal response:**

> **Question:** What is the capital of France?
>
> **System response:**
> I don't have enough information in the provided reviews to answer that question.

The refusal fires because the retrieved chunks contain no information about France or European capitals. Rule 2 in the system prompt provides the exact refusal string, so the model produces a consistent, predictable response rather than guessing or fabricating.

---

## Query Interface

**Interface description:**

The app uses Gradio's `Blocks` layout with two output fields:

| Field | Type | Description |
|-------|------|-------------|
| Your question | Text input | Free-text question about any Wright College CS professor |
| Answer | Text output (8 lines) | LLM-generated response, grounded in retrieved reviews, ending with a "Sources:" citation list |
| Retrieved from | Text output (4 lines) | Deduplicated list of source `.txt` files returned by the retrieval step, shown independently of the LLM output |

The query is submitted either by clicking the **Ask** button or pressing Enter in the question box.

**Sample interaction transcript:**

```
Question: What should a student expect regarding the workload, homework,
          and exams in Professor Khan's classes?

Answer:
Based on the provided reviews, a student can expect a varying level of workload
and homework in Professor Khan's classes. Some reviewers mentioned that the
assignments online are easy and there's no way you can't get a 100, while others
stated that there's lots of homework. Specifically, one reviewer mentioned that
Professor Khan gives weekly assignments.

Regarding exams, some reviewers found them to be hard, with one mentioning that
quizzes and exams are hard but assignments are easy. Another reviewer mentioned
that Professor Khan has 2 exams, a midterm and a final, and it's crucial to do
well on them.

The difficulty level of the classes also varied, with ratings ranging from 1.0 to
5.0. However, most reviewers agreed that the lectures can be long and boring, with
some students finding ways to complete assignments during class time and even dozing
off.

Sources: Abdul_Khan.txt

Retrieved from:
• Abdul_Khan.txt
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professor or professors have the highest overall ranking? | Dan Grigoletti and Douglas Kaniuk [expected failure case, answering correctly would have required calculating averages of ranking] | Based on the provided reviews, several professors have the highest overall ranking of 5.0: Duke Best, Dan Grigoletti, Erika Nadas, Abdul Khan, and Douglas Kaniuk. These professors have received perfect scores from their students, indicating exceptional teaching and overall quality. | Partially relevant | Partially accurate |
| 2 | How does Professor Best connect his coursework to the real world and the tech industry? | Professor best brings in outsides speakers, talks about his experience in industry, and encourages self-guided learning. | Professor Best integrates real-world tech industry applications and guest speaker insights into his coursework while encouraging students to extend their learning beyond textbooks. | Relevant| Accurate |
| 3 | What should a student expect regarding the workload, homework, and exams in Professor Khan's classes? | Lots of homework, reading, and some students mention difficult exams.| Students in Professor Khan's classes should prepare for a heavy workload consisting of reading and weekly assignments, as well as challenging exams. | Relevant | Accurate |
| 4 | How does Professor Khan typically deliver his lectures? | Should mention PowerPoint, reading from textbooks. Many reviews state he does not explain things clearly. | Reviews indicate that Professor Khan delivers lengthy, continuous lectures primarily by reading directly from PowerPoints or textbooks, often without sufficiently explaining or illustrating the material. | Relevant | Accurate |
| 5 | What do students say about the textbook used in Professor Haji's class? | Professor's self written textbook is formatted in such a way that many students find it hard to engage with, specifically with CIS144. | While textbook requirements vary across his classes, students who used Professor Haji's self-written textbook heavily criticized it for being visually chaotic, full of errors, and very difficult to read. | Relevant | Accurate |

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
Which professor or professors have the highest overall ranking?

**What the system returned:**
Both Professor Duke Best and Professor Dan Grigoletti have the highest overall ranking of 5.0.

**Root cause (tied to a specific pipeline stage):**
Generation was incapable of viewing all reviews to take the average of scores to return the highest. The LLM is just incapable of doing such functions without more sophisticated tool calling.

**What you would change to fix it:**
Design a deterministic harness that is part of the ingestion phase that can properly extract review scores, average them, and then append them to a chunk in the same way the Professor's name is appended. Then add a metadata filtering component to the pipeline that allows that information to be readily accessed.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Taking the time to develop the spec helped me to understand the end result much better. I had a better idea of what to look for in terms of the specific functions and how they should work. I imagine that the spec helped streamline the code development process, though I can't say for certain as I didn't do a control prompt without the spec.


**One way your implementation diverged from the spec, and why:**
My spec planned to extract the professor's name from the filename and prepend it to the chunk text to improve semantic context, alongside basic source metadata. During implementation in ingest.py, I diverged by also isolating the extracted professor's name into its own dedicated metadata key ("professor": professor). I did this because while the prepended text helps the embedding model, the isolated metadata key allows the vector database to perform exact-match filtering, setting the architecture up to support advanced search features later.


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

- *What I gave the AI:* I asked how to handle a retrieval edge case where a query about Professor Best returned one chunk about Professor Grigoletti in the top 5. I asked if I needed an embedding level fix or if the generation step would safely ignore it.
- *What it produced:* The AI validated my assumption but also generated a code snippet to implement a max_distance threshold filter inside the retrieve_context function to explicitly drop weak semantic matches.
- *What I changed or overrode:* I chose to reject the AI's threshold code. I decided to rely on the LLM system prompt to naturally filter out the irrelevant Grigoletti chunk during generation. Hardcoding a distance threshold was unnecessary and could risk breaking future queries that intentionally compare multiple professors.


**Instance 2**

- *What I gave the AI:* While planning the ingestion pipeline, we discussed using a zero overlap \n\n chunking strategy to keep individual reviews intact.
- *What it produced:* The AI suggested adding a secondary character splitter to my ingestion script to catch massive outlier reviews that might exceed the all-MiniLM-L6-v2 embedding token limit.
- *What I changed or overrode:* I reviewed my raw text files and verified that the absolute longest review in my dataset was only 600 characters, which fits safely inside the token limit. I overrode the AI's suggestion and kept my ingestion script strictly limited to the \n\n split, keeping the codebase lightweight and avoiding unnecessary edge case logic.

---

## Metadata Filtering (stretch goal)

The interface includes an optional "Filter by Professor" dropdown that restricts retrieval to a single professor's reviews before the similarity search runs. This is implemented as a ChromaDB `where` filter on the `professor` metadata field, which was stored alongside every chunk during the embedding phase.

**How it works:**
1. The Gradio dropdown lists all 10 professors plus a default "All Professors" option, derived dynamically from the `documents/` directory.
2. When a specific professor is selected, `retrieve_context()` passes `where={"professor": "Professor Name"}` to the ChromaDB query, restricting the candidate pool to only that professor's chunks.
3. When "All Professors" is selected, no `where` filter is applied and behavior is identical to the base pipeline.

**Visible effect — same query, different filter settings:**

Query: *"What is their lecture style like?"*

| Setting | Sources returned | Answer scope |
|---------|-----------------|--------------|
| All Professors | Abdul_Khan.txt, Duke_Best.txt, Gustavo_Alatta.txt, Ogar_Haji.txt | Compares lecture styles across four professors |
| Filter: Abdul Khan | Abdul_Khan.txt only | Focused exclusively on Khan's lecture delivery |

**Full responses:**

*All Professors:*
> The lecture styles of the professors vary. Professor Gustavo Alatta's lectures are described as "basically demonstrations for the work you will do" and "amazing," making it simple for students to understand and complete the work. Professor Abdul Khan's lectures are criticized for having "lots of mistakes" and an inability to keep up with system updates. Professor Duke Best is praised for breaking down "hard to understand concepts" into "bite-sized pieces" and being "very intuitive" to students' learning journeys. Professor Laurie Alfaro's lectures are described as "amazing" and she is praised for being "super supportive and helpful." Professor Ogar Haji's lectures are based on the textbook, but his strong accent and fast pace can make it hard for students to understand the information.
>
> Sources: Gustavo_Alatta.txt, Abdul_Khan.txt, Duke_Best.txt, Laurie_Alfaro.txt, Ogar_Haji.txt

*Filter: Abdul Khan:*
> Professor Abdul Khan's lecture style is often described as simply reading from a notepad, PowerPoint, or the textbook, without much explanation or illustration. He sometimes gets confused and makes mistakes during presentations. One review also mentions that his lectures are long. Additionally, it's noted that he often uses a "copy and paste" approach to his presentations. Overall, his lecture style seems to be more of a straightforward reading from prepared materials rather than engaging with the students or providing in-depth explanations.
>
> Sources: Abdul_Khan.txt

---

## Conversational Memory (stretch goal)

The interface uses `gr.ChatInterface`, which maintains a running conversation history across turns. On each new message, the full prior exchange is included in the Groq API call alongside fresh retrieved context for the current question. This allows the LLM to resolve pronouns and implicit references from earlier turns.

**How it works architecturally:**

The Groq messages array is built as:
```
[system_prompt] + [prior_turns_from_history] + [current_user_message_with_retrieved_context]
```

Context is retrieved only for the current question — not re-injected into historical turns. This keeps token usage low while still giving the LLM enough evidence to answer the current question and the conversation thread to resolve any pronoun references.

**Multi-turn exchange demonstrating pronoun resolution:**

> **Turn 1**
> User: Tell me about Professor Khan's lecture style.
>
> Assistant: Professor Khan's lecture style is often described as reading from PowerPoint or the textbook, with some students mentioning that he doesn't explain things well or illustrate concepts on the board. He sometimes gets confused and makes mistakes during lectures. His accent is also frequently mentioned as being thick and hard to understand. Some students found the lectures to be boring and didn't see the need to attend class, as they could learn the material on their own or by reading the textbook.
>
> Sources: Abdul_Khan.txt

> **Turn 2**
> User: How is his workload and homework compared to those lectures?
>
> Assistant: According to the reviews, Professor Khan's workload and homework are often described as having weekly assignments, and some students found the online assignments to be easy. However, quizzes and exams are mentioned as being hard. In one review, it's mentioned that having a source of all the quizzes and exams made the class easy for the student. Another review mentions that there is no way you can't get a 100 on the assignments online, but the quizzes and exams are a different story.
>
> Sources: Abdul_Khan.txt

In Turn 2, "his" is never defined — the system resolves the pronoun to Professor Khan from the prior turn's context, and the fresh retrieval correctly returns Khan's chunks to ground the answer.

---

## Chunking Strategy Comparison (stretch goal)

Two chunking strategies were evaluated on the same 10 source documents using the same embedding model (`all-MiniLM-L6-v2`) and a retrieval depth of Top-k: 3.

| Strategy | Description | Chunk count |
|----------|-------------|-------------|
| **Paragraph split** (original) | Split on `\n\n`; each chunk is one complete review | 91 |
| **Naive fixed split** | Sliding window of 200 characters, 20-character overlap, ignores all boundaries | 205 |

The naive strategy was implemented in `compare_chunking.py`, which builds a separate ChromaDB collection (`naive_reviews`) and runs the same queries against both collections so results can be compared directly.

**Why the naive split is harmful:** Every `.txt` source file contains structured review records separated by blank lines. A fixed-character window is completely unaware of these boundaries. The result is that chunks routinely begin or end mid-word ("ass: Yes" from "Online Cl**ass**: Yes", "lighted words" from "high**lighted** words"), mid-sentence thoughts lose their head or tail, and in some cases two entirely separate reviews are merged into one retrieval unit. An LLM receiving a fragment that begins mid-word cannot reliably synthesize it into a coherent answer.

---

### Query 1: What do students say about the textbook used in Professor Haji's class?

| Rank | Paragraph split — Source | Distance | Naive split — Source | Distance |
|------|--------------------------|----------|----------------------|----------|
| 1 | Ogar_Haji.txt | 0.2403 | Ogar_Haji.txt | 0.2829 |
| 2 | Ogar_Haji.txt | 0.3349 | Ogar_Haji.txt | 0.3252 |
| 3 | Ogar_Haji.txt | 0.3564 | Ogar_Haji.txt | 0.3531 |

**Paragraph split — Rank 1 chunk:**
```
Professor: Ogar Haji
Quality
1.0
...
Professor uses his own self written "textbook", which is ridden with grammar errors and poor
English, multiple horrible contrasting colors, different sized fonts, and highlighted words
which makes it very hard to read (not to mention the excessive clipart). Knowing I'm going
to strain my eyes with this "textbook" makes me feel discouraged.
Get ready to read  Participation matters  Lecture heavy
```

**Naive split — Rank 1 chunk:**
```
Professor: Ogar Haji ass: Yes Professor uses his own self written "textbook", which is
ridden with grammar errors and poor English, multiple horrible contrasting colors,
different sized fonts, and highlighted words which
```

**Analysis:** The paragraph split returns a complete, self-contained review as its top result — the full textbook complaint is intact, beginning with the reviewer's scores and ending with their tag words. The naive split's top result opens with `ass: Yes`, the trailing fragment of "Online Cl**ass**: Yes", followed by the same textbook sentence — but the sentence is cut off before its conclusion. The naive Rank 3 chunk opens with `lighted words` (the second half of "high**lighted** words"), making it nearly unusable without the sentence that precedes it. The paragraph strategy clearly wins on completeness.

---

### Query 2: How does Professor Best connect his coursework to the real world and the tech industry?

| Rank | Paragraph split — Source | Distance | Naive split — Source | Distance |
|------|--------------------------|----------|----------------------|----------|
| 1 | Duke_Best.txt | 0.4147 | Duke_Best.txt | 0.3785 |
| 2 | Duke_Best.txt | 0.4206 | Duke_Best.txt | 0.3853 |
| 3 | Duke_Best.txt | 0.4362 | Duke_Best.txt | 0.4065 |

**Paragraph split — Rank 3 chunk (most directly answers the question):**
```
Professor: Duke Best
Quality
5.0
...
Professor was highly devoted to helping us understand concepts and real life application.
We had great speakers in the industry that provided career path feedback. I appreciated
the help on topics and his professionalism.
Inspirational  Hilarious  Accessible outside class
```

**Naive split — Rank 1 chunk:**
```
Professor: Duke Best ities of his I really admire are his passion for (teaching and
technology) and his selflessness. He is more than willing to go the extra mile to help
students succeed in his class and beyond it as wel
```

**Analysis:** The naive strategy actually produces lower (better) raw distance scores on this query, which might appear at first glance to be a win. But the content tells the opposite story. The naive Rank 1 chunk begins mid-word — `ities of his` is the tail of `qual**ities** of his` — and ends mid-word at `as wel` (from `as well`). An LLM reading this chunk cannot extract a complete thought. The paragraph strategy's Rank 3 chunk is the definitive answer: it contains the specific claim about "great speakers in the industry that provided career path feedback" as a fully intact sentence. This query illustrates an important principle: cosine distance measures embedding similarity, not answer quality. A fragment can embed close to a query while still being too broken to generate a coherent response from.

---

### Query 3: What should a student expect regarding the workload, homework, and exams in Professor Khan's classes?

| Rank | Paragraph split — Source | Distance | Naive split — Source | Distance |
|------|--------------------------|----------|----------------------|----------|
| 1 | Abdul_Khan.txt | 0.2796 | Abdul_Khan.txt | 0.3009 |
| 2 | Abdul_Khan.txt | 0.3427 | Abdul_Khan.txt | 0.3430 |
| 3 | Abdul_Khan.txt | 0.3529 | Abdul_Khan.txt | 0.3449 |

**Paragraph split — Rank 1 chunk:**
```
Professor: Abdul Khan
Quality
1.5
Difficulty
2.0
Class: CIS120
Nov 9th, 2015
...
Lectures are long. Has accent. Sometimes gets confused. For me the class is easy because
I have a source of all the quizzes and exams. Overall. Assignments online are easy. There
is no way you cant get a 100. quizzes and exams are hard. You will need the book.
```

**Naive split — Rank 1 chunk:**
```
Professor: Abdul Khan ve to get by. Grade is 30% homework/lab coding assignments (6 of
each), 10% quizzes, 30% midterm exam, 30% final exam. Class was hybrid so we met every
other week. Get ready to read Test heavy Clear g
```

**Analysis:** The naive Rank 1 chunk opens with `ve to get by` — the end of `ha**ve** to get by` — and ends with `Clear g`, cutting off the tag word `Clear grading criteria`. The middle of the chunk happens to include a specific grade breakdown (30% homework, 10% quizzes, 30% midterm, 30% final) that does not appear as cleanly in the paragraph strategy's top result. However, this information is stranded between two damaged sentence fragments, making it harder for the LLM to interpret reliably. The paragraph strategy's Rank 1 chunk, by contrast, is a complete review — every statement from the reviewer has its beginning, middle, and end intact — giving the LLM the full context it needs to summarize workload expectations accurately.

---

**Overall conclusion:** The paragraph-split strategy outperformed the naive fixed split on all three queries. The fundamental problem with the naive approach is that it treats the documents as undifferentiated character streams. Because each source file is composed of discrete, self-contained review blocks separated by `\n\n`, splitting on those natural boundaries perfectly aligns chunk boundaries with semantic boundaries. The naive split violates those boundaries consistently: every chunk except the very first begins with a sentence fragment from the previous review and ends with a sentence fragment that continues in the next chunk. A lower cosine distance score does not compensate for a chunk that an LLM cannot interpret without its missing head or tail.

---

## Hybrid Search (stretch goal)

The retrieval pipeline was upgraded from pure semantic search to hybrid search by combining ChromaDB cosine-distance retrieval with BM25 exact-keyword retrieval, merged using Reciprocal Rank Fusion (RRF).

**How it works:**

1. At app startup, `build_bm25_index(collection)` in `embed.py` calls `collection.get()` to fetch every stored document and tokenizes each with `.lower().split()`, building a `BM25Okapi` corpus that is guaranteed to be identical to the vector store.
2. On each query, `retrieve_context()` runs both searches in parallel, fetching up to 20 candidates from each method to give the fusion algorithm sufficient signal.
3. Both searches respect the professor dropdown filter: ChromaDB uses its native `where={"professor": ...}` clause, while BM25 pre-filters its in-memory corpus to only that professor's tokenized documents before scoring.
4. RRF assigns each document a score of `1 / (60 + rank)` from each list it appears in, sums the contributions, and returns the top 5 by combined score. 

**Why RRF?** It is rank-based rather than score-based, so it sidesteps the problem of semantic distances and BM25 scores being on completely different mathematical scales. 

---

### Query Comparison: Semantic vs. Hybrid Generation

To evaluate the hybrid architecture, I tested queries that specifically expose the blind spots of vector databases (like alphanumeric course codes) and pure keyword matching (like subjective, abstract concepts). 

---

**Query 1 (Exact Keyword Match):** "What is CIS142 like?"

* **The Retrieval Challenge:** "CIS142" is an alphanumeric course code with no intrinsic semantic meaning. A pure vector search struggles here because it treats the code as an abstract token, sometimes returning chunks for completely different classes like "CIS103" simply because the reviews share similar sentence structures.
* **How Hybrid Performed:** BM25 easily anchored onto the exact string "CIS142" and RRF boosted those chunks to the top, completely overriding the semantic search's confusion.
* **The Generated Response:**
> CIS142 is taught by two professors mentioned in the reviews: Abdul Khan and Gustavo Alatta. According to the reviews, Abdul Khan's CIS142 class has varying quality ratings (1.0 and 3.0) and difficulty ratings (1.0 and 5.0). One review mentions that the professor often makes mistakes during presentations, and the material is copied and pasted, but the student learned more on their own. Another review of Abdul Khan's class mentions a strong accent, 2-hour lectures, and 2-hour labs, with weekly assignments and two exams.
> 
> On the other hand, Gustavo Alatta's CIS142 class has a quality rating of 5.0 and varying difficulty ratings (2.0, 3.0, and 4.0). The reviews praise Professor Alatta for his hands-on projects, lectures, and desire for students to succeed. He is described as knowledgeable, caring, and accessible outside of class. However, one review mentions that the class requires self-studying, especially for those with no prior coding experience, and that the professor is strict about deadlines.
>
> Sources: Abdul_Khan.txt, Gustavo_Alatta.txt

---

**Query 2 (Conceptual Search):** "Who is the most inspiring professor?"

* **The Retrieval Challenge:** "Inspiring" is an abstract, subjective sentiment. Pure BM25 keyword matching fails here because students rarely use the exact word "inspiring"—instead using phrases like "Godsend," "went the extra mile," or "changed my career path."
* **How Hybrid Performed:** Since "inspiring" is a concept rather than a literal keyword, BM25 returned noisy, irrelevant chunks. The semantic engine correctly identified sentiment-rich synonyms like "amazing" and "inspirational," allowing RRF to filter out the keyword-based noise and surface the most conceptually relevant reviews.
* **The Generated Response:**
> Based on the provided reviews, several professors are described as inspirational, including Duke Best, Laurie Alfaro, and Mohammed Hossain. Duke Best is consistently praised for his inspirational teaching style, with multiple reviews describing him as inspirational and amazing. Laurie Alfaro is also described as inspirational, with one review stating that she is "EXCELLENT" and another mentioning that she is inspirational despite some drawbacks in her teaching style. Mohammed Hossain is described as inspirational in some reviews, but also receives criticism in others. Overall, it seems that Duke Best is the most consistently inspirational professor, but Laurie Alfaro and Mohammed Hossain are also praised for their inspirational teaching styles.
>
> Sources: Duke_Best.txt, Laurie_Alfaro.txt, Mohammed_Hossain.txt

---

**Query 3 (Student Jargon/Slang):** "Is the homework mostly busywork?"

* **The Retrieval Challenge:** This query relies on "busywork", a highly specific piece of student slang. 
* **How Hybrid Performed:** "Busywork" is niche slang that pure semantic search often misses. BM25 successfully anchored on the exact slang term, while the semantic engine captured broader "workload" context. Fusing these signals provided a balanced, well-rounded set of reviews for the LLM to synthesize.
* **The Generated Response:**
> Based on the provided reviews, opinions about the homework vary. Some professors' homework is described as "useful to better understand the content" (Douglas Kaniuk, CIS103), "fun to do and solve" (Douglas Kaniuk, CIS103), and "helpful" (Ogar Haji, CIS144). However, others describe the homework as "horrible" (Ogar Haji, CIS120), "lots and lots of homework" (Ogar Haji, CIS144), or "makes no sense" (Ogar Haji, CIS120). It seems that whether the homework is considered busywork depends on the professor and the specific class.
>
> Sources: Douglas_Kaniuk.txt, Ogar_Haji.txt, Abdul_Khan.txt, Laurie_Alfaro.txt

---

**Overall conclusion:** Hybrid search out-performs either method alone because it allows the two retrieval systems to cover each other's blind spots. The conversational query router (which rewrites follow-up questions) ensures that the BM25 index always receives exact names and course codes to anchor onto, while the semantic vector database successfully pulls conceptually related sentiment, resulting in a perfectly grounded final generation.
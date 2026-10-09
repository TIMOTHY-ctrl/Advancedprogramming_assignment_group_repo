# Bus seat booking coursework

Python 3.10+; standard library only. Run commands from the repository root.

```powershell
python -B -m unittest discover -s test -v
python -B -m src.main
```

## Submission files

- `presentation/coursework-slides.pptx`: exactly 15 slides, editable in PowerPoint.
- `presentation/coursework-slides.pdf`: PowerPoint-exported copy for submission or printing.
- `presentation/coursework-slides.html`: the same slides for a browser; arrow keys navigate and printing produces 15 pages.
- `test/test_architecture.py`: exactly eight tests, identified T1-T8.
- `evidence/test-results.txt`: actual full test output.
- `evidence/tdd-red.txt`, `evidence/tdd-green.txt`: actual failing and passing runs of T4.
- `evidence/tdd-change.diff`: the scheduling policy and use-case integration added after the failing run.
- `evidence/console-smoke.txt`, `evidence/architecture-dependencies.txt`: console walkthrough and inspected import dependencies.
- `src/`: final implementation with in-memory persistence.

Slide 1 lists the four confirmed members and their student numbers. ATUHAIRE MARY SEANICE is Domain Lead; kisakye rita is Domain Model Lead; Nassaka Catherine is Architecture Lead; Mwizerwa Timothy covers Testing and Integration. The coursework specifies five members; confirm the four-member arrangement with the instructor or add the fifth member when confirmed.

To regenerate both decks after editing `tools/build_slides.py`, install the build-only dependency with `python -m pip install -r tools/requirements.txt`, then run `python -B tools/build_slides.py`. The application and tests do not need this dependency.

On Windows with PowerPoint installed, run `powershell -File tools/export_slides.ps1` to refresh the PDF and preview images after editing the deck.

AI disclosure: OpenAI Codex helped review the rubric, revise the domain model and implementation, write tests, capture TDD evidence, and prepare slides. Every member must review and be able to explain the submitted work.

## Six rules and scope

The authoritative BR1-BR6 statements, responsible components, and violation outcomes are on Slide 3; Slide 15 maps them to code and tests. Booking a seat and withdrawing its advertisement are the two event-connected use cases. Scheduling, lookup, and listing are small supporting operations.

The scheduling policy prevents equal departure instants for the same bus; journey duration and overlapping journeys are outside scope. All times supplied by the console are local, timezone-naive values. Persistence lasts for one process only.

## TDD evidence

T4 was written and executed against the original scheduling behaviour, after repairing imports. It genuinely failed with `AssertionError: ValueError not raised`. The domain scheduling policy and its invocation from `CreateTripService` were then added. The same test passed, and the final eight-test suite passed. This is a new TDD cycle performed during this revision, not a claim about how the original project was developed. Regenerating slides does not rerun or overwrite these historical logs.

## Design decisions

`Trip` owns booking creation and exposes a read-only booking collection. `TripAdvertisement` owns its active-to-withdrawn transition and returns a new immutable state. Repositories retain withdrawn advertisements while listing only active advertisements. Replaying a full-booking event returns an explicit rejection without changing either aggregate. Missing advertisements also return a rejection. The booking remains committed if the follow-up rejects; the DTO exposes the outcome. This small in-process example has no distributed transaction, retries, or message broker.

No Factory is needed: constructors validate small inputs. No Layer Supertype is used: there is no shared entity behaviour requiring a common domain base class. Repository ABCs are contracts, not a domain Layer Supertype.

Group rubric evidence can be completed here; individual marks require each member to explain concepts, defend placement, trace a use case, and discuss a rule change during assessment. No score is guaranteed.

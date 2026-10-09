# Bus seat booking coursework

Python 3.10+; standard library only. Run commands from the repository root.

For direct file execution in VS Code, install the project once in the active
virtual environment with `python -m pip install -e .`. This uses setuptools
during installation; the application itself has no third-party runtime dependencies.
Repeat the installation if you recreate the virtual environment or move the project.

```powershell
python -B -m unittest discover -s test -v
python -B -m src.main
```

## Submission files

The presentation folder was removed at the group's request. The coursework still requires a 15-slide deck, which must be supplied separately.

- `test/test_architecture.py`: exactly eight tests, identified T1-T8.
- `evidence/test-results.txt`: actual full test output.
- `evidence/tdd-red.txt`, `evidence/tdd-green.txt`: actual failing and passing runs of T4.
- `evidence/tdd-change.diff`: the scheduling policy and use-case integration added after the original failing run.
- `evidence/isolation-red.txt`, `evidence/isolation-green.txt`: the second genuine TDD cycle, fixing repository aliasing.
- `evidence/isolation-change.diff`: implementation and test changes for the isolation revision.
- `evidence/typecheck-results.txt`: static verification of source types and injected protocol implementations.
- `evidence/console-smoke.txt`, `evidence/architecture-dependencies.txt`: console walkthrough and inspected import dependencies.
- `src/`: final implementation with in-memory persistence.

The four confirmed members are ATUHAIRE MARY SEANICE (Domain Lead), kisakye rita (Domain Model Lead), Nassaka Catherine (Architecture Lead), and Mwizerwa Timothy (Testing and Integration). The coursework specifies five members; confirm the four-member arrangement with the instructor or add the fifth member when confirmed.

The slide-generation tools were also removed. The application and tests require no third-party packages.

AI disclosure: OpenAI Codex helped review the rubric, revise the domain model and implementation, write tests, capture TDD evidence, and prepare slides. Every member must review and be able to explain the submitted work.

## Six rules and scope

The separately supplied deck must state BR1-BR6, responsible components, and violation outcomes on Slide 3, and map rules to code and tests on Slide 15. Booking a seat and withdrawing its advertisement are the two event-connected use cases. Scheduling, lookup, and listing are small supporting operations.

The scheduling policy prevents equal departure instants for the same bus; journey duration and overlapping journeys are outside scope. All times supplied by the console are local, timezone-naive values. Persistence lasts for one process only.

## TDD evidence

T4 was written and executed against the original scheduling behaviour, after repairing imports. It genuinely failed with `AssertionError: ValueError not raised`. The domain scheduling policy and its invocation from `CreateTripService` were then added. The same test passed, and the final eight-test suite passed. This is a new TDD cycle performed during this revision, not a claim about how the original project was developed. A second cycle added a failing T2 isolation assertion (stored availability incorrectly became zero before save), then introduced detached repository roots and transactions. The final T2 was expanded to check save and identity behaviour too. Regenerating slides does not rerun or overwrite historical logs.

## Design decisions

`Trip` owns booking creation and exposes a read-only booking collection. `TripAdvertisement` owns its active-to-withdrawn transition and returns a new immutable state. Repositories retain withdrawn advertisements while listing only active advertisements. Replaying a full-booking event returns an explicit rejection without changing either aggregate. Missing advertisements also return a rejection. The booking remains committed if the follow-up rejects; the DTO exposes the outcome. Storage exceptions roll back both aggregate writes and the departure index through an injected UnitOfWork. A returned domain rejection is distinct from an exception. This in-process example has no distributed transaction, retries, or message broker.

No Factory is needed: constructors validate small inputs. No Layer Supertype is used: there is no shared entity behaviour requiring a common domain base class. Repository ABCs are contracts, not a domain Layer Supertype.

Group rubric evidence can be completed here; individual marks require each member to explain concepts, defend placement, trace a use case, and discuss a rule change during assessment. No score is guaranteed.

## Change, reuse, and concurrency

- SRP/MVC: ConsoleApp handles input routing through ConsolePresenter; ConsoleView implements that protocol; domain roots own rules; application services coordinate.
- DIP/ISP/OCP: small SchedulingPolicy, AdvertisementUpdater, FullyBookedHandler, and UnitOfWork protocols permit replacement without modifying callers. Constructors do not instantiate concrete application collaborators.
- LSP/polymorphism: T6 runs the same repository behaviour and complete booking flow against the indexed production adapter and an independent scan-based reference adapter. T5 substitutes updater/handler objects without subclassing.
- Encapsulation/identity: Trip returns a read-only booking view; repository reads, additions, and saves detach Trip state. Entities compare and hash by identity; SeatNumber compares by value. Frozen Trip fields do not imply deep immutability.
- Outcomes: enum-backed AdvertisementOutcome separates success/rejection status from its reason; the view owns display formatting.
- Atomicity: both adapters and the UnitOfWork must share the same InMemoryStore, as wired in main.py. The lock spans each write use case from lookup to follow-up. Nested handler calls are reentrant. Exceptions restore roots and the bus/departure index; no partial booking or orphan advertisement survives.
- Concurrent correctness: T3 races same-seat bookings, T4 races bus assignments, and T7 races different seats. T8 injects failures after writes and verifies freshly retrieved state. Workflows run through services; detached manual read/modify/save sequences must also use UnitOfWork to avoid lost updates.
- Performance: an index avoids scanning all trips for a bus/departure conflict. Dictionary snapshots remain O(number of stored roots); locking serializes writers. This is appropriate for the required small single-process system, not a claim of multi-process or production scalability. A future database adapter needs matching transaction/locking semantics; inheritance alone cannot supply them.

The eight required test methods are scenario groups; subcases add regression coverage without inventing additional BR identifiers. Four confirmed members still cover five roles; instructor acceptance and individual oral defence cannot be supplied by code.

Optional static check (development dependency only): install `mypy==2.4.0` in a development environment, then run `python -m mypy --follow-imports=normal --check-untyped-defs --explicit-package-bases src`. The recorded run found no issues in all 28 source files.

## Concepts to explain during assessment

| Concept | Evidence and design reason |
| --- | --- |
| Ubiquitous Language | Trip, Bus, Booking, SeatNumber, Fully Booked, and Advertisement Withdrawal are shared across BR1-BR6, source, tests, and slides. The aggregate package is TripAdvertisementAggregate. |
| Tactical DDD | Two roots protect their own invariants; Booking belongs to Trip; SeatNumber is a Value Object; BusSchedulingPolicy spans trips; TripFullyBooked requests B's action; repositories store roots. |
| Decorators | @dataclass generates object boilerplate; @property exposes computed state; @abstractmethod defines repository obligations; @contextmanager implements exception-safe transactions. Decorators wrap or transform definitions; they are not inheritance. |
| Composition and caller | main constructs collaborators and injects them. BookSeatService is the caller of repository/updater contracts; implementations are replaceable objects, not superclass requirements. |
| Functional programming | The scheduling policy checks inputs without mutating them, any uses a generator expression, callbacks are passed as values, and advertisement transitions return new immutable state. The whole program is intentionally not purely functional: booking and storage change state. |
| Abstraction and polymorphism | ABCs specify repository contracts; Protocols specify structural use-case, policy, handler, transaction, and presenter contracts. T5/T6 exercise substitutes, not merely matching method names. |
| Substitutability / variance | An implementation must accept every input its contract allows and preserve outcomes/invariants. Callable parameter types are contravariant and return types covariant: an output callback accepting object can consume each str produced by the view. No invented generic hierarchy is needed to illustrate this. Mutable list is invariant; Iterable is read-only and covariant. |
| SOLID | Responsibilities are separated; ports permit extension; adapter contracts are tested; interfaces expose workflow-specific operations; callers depend on injected abstractions. No claim that every future requirement can be added without changes. |
| Monad | Not implemented or required by the coursework. AdvertisementOutcome is an enum-backed result DTO, not a monad: it has no bind operation or demonstrated monad laws. Adding that machinery would not improve this synchronous workflow. |
| Factory / Layer Supertype | Deliberately omitted: creation is simple and there is no shared domain behaviour needing a superclass. Interface inheritance through repository ABCs is sufficient. |

Type hints describe contracts; Python does not enforce them at runtime. Domain values also validate inputs. Constructor injection supplies objects; dependency inversion determines which layer owns the contracts. A source dependency can point inward while a runtime call reaches an outward adapter.

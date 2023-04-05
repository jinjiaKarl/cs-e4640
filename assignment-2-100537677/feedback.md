This grade is provisional. Why: we need to cross-check all assignments and maybe a face-to-face question to finalize the grade. We also do check the assignments w.r.t. the rule after releasing this grade. In principle, the final grade will be fixed at the end of the course. If you have any feedback, you can send it.

 

----------------

 

Overall Grade: 24.75

 

Overall comments: The design of manager and ingestapp for both batchingest and streamingingest are all wrong, the manager should invoke ingestapp as blackbox and the ingest app would do the actual work with data. The tests used for profile performance is not sufficient for a big data problem, as the through put was not actually measured with insufficient amount of data.

 

Requests for face-to-face explanation:

Yes, why do you have set_args() in some files which shouldn’t take arguments, and they are not called them with arguments either?

 

-----------------

Part 1 (weighted factor=3, max 15 points):

 

10

 

Point 1.1

 

A set of constraints for files to be ingested (attribute names, possible values, meaning):

 

A configuration model for the tenant service profile (structure):

 

Explain why for such constraints from the platform provider viewpoint:

 

Implement these constraints (configurable/flexible) and examples:

 

3

 

Point 1.2

 

Explain the design of **clientbatchingestapp**  - the flow/interface/architecture/technologies: 0

 

Explain the design of **clientbatchingestapp**  - internal logic/ingestion/data wrangling: 0

 

 

Provide one implementation - the internal logic/data wrangling: 0.75 

Provide one implementation - the input/output, execution model: 0.75

 

1.5

The design of the clientbatchingestapp and mysimbdp-batchingestmanager is wrong.

The clientbatchingestapp needs to follow the guideline in the next Point 3 (work as a blackbox), it needs to do the scanning.

And no explanation on how to interact with other components, how to scan for files, how to ingest.

You should describe the flow more detailed besides defining the components.

 

Point 1.3

 

Design  **mysimbdp-batchingestmanager** - the flow/interface/architecture/technologies: 0

 

Design **mysimbdp-batchingestmanager** - support multiple apps/tenants/integration models with apps: 0.75

 

Implement **mysimbdp-batchingestmanager** (especially how does it support "blackbox" apps): 0

 

Explain **mysimbdp-batchingestmanager** schedules (given the availability of files): 0

 

0.75

The purpose of mysimbdp-batchingestmanager was completely misinterpreted, you designed as what clientbatchingestapp was supposed to do.

The mysimbdp-batchingestmanager works on the platform side, it invokes clientbatchingestapp the tenants provided according to schedule, mysimbdp-batchingestmanager should not monitor the folders or does any actually work related to data. Also, as it does not know anything about the clientbatchingestapp (black box), which means it cannot call clientbatchingestapp with any argument.

 

Point 1.4

 

Explain the multi-tenancy  model in **mysimbdp**: 0.75

 

Develop test programs (**clientbatchingestapp**): 0

 

Develop test data and test profiles for tenants (min 2 different tenants):0.5

 

Show the performance of ingestion tests (min 2 different tenants), violation of constraints, ingestion amount per second: 0.5

 

1.75

 

The clientbatchingestapp was wrong.

The test for performance with 10M data is not enough to show the big data problem.

 

 

Point 1.5

 

Explain logging features w.r.t. metrics, successful/failed operations: 0.75

 

Explain how logging information stored in separate files/databases, etc.: 0.75

 

Implement the logging features: 0.75

 

Provide and explain statistical data extracted from logs  for individual tenants/whole system: 0.75

 

3

 

Part 2 (weighted factor=3, max 15 points):

 

8.75

 

Point 2.1:

 

Explain the multi-tenancy model - shared/dedicated parts: 1.5

 

Explain the multi-tenancy model - the logic/correctness: 1

 

2.5

Database also need to reflect different tenants along with messaging system.

 

Point 2.2

 

Design **mysimbdp-streamingestmanager** - features: 0

 

Design **mysimbdp-streamingestmanager** - integration/execution models for  apps (for multitenant, configuration, ...): 0.75

 

Implement **mysimbdp-streamingestmanager** - features: 0

 

Implement  **mysimbdp-streamingestmanager** - integration/execution models (configuration/tightly vs loosely coupling): 0.75

 

1.5

The design of the model is wrong.

The mysimbdp-streamingestmanager is on the platform side, tt should invoke clientstreamingestapp(black box) which should listen on the topics and consume data and ingest.

As mysimbdp-streamingestmanager is on the platform side, tenants are not able to call it with arguments, the messaging system should be configurated to match between clientstreamingestapp(consumer) and a publisher which tenants own.

 

 

Point 2.3.

 

Develop test ingestion programs, wrangling (**clientstreamingestapp**): 0.5

 

Develop test data, and test profiles for tenants: 0.75

 

Perform ingestion tests (min 2 tenants): 0.5

 

Explain tests: 0.25

 

2

Failure and exceptions are not shown.

The test and performance was not explained. You should run the performance with something that can demonstrate big data problem, the published data from two csv files is not enough to profile the through put.

 

Point 2.4.

 

Design metrics to be reported/collected: 0.75

 

Explain metrics and reporting mechanism: 0.75

 

Design the report format: 0

 

Explain possible components/flows for reporting: 0

 

1.5

Only provided metrics without explaining measurement, reporting format, interesting component, and flow.

For example, ingestion_time, avg_ingestion_time is calculated wrong. As the insert_once() call it  non-blocking.

 

Point 2.5.

 

Implement the feature in **mysimbdp-streamingestmonitor**:

 

 

Design the notification mechanism - constraints/when: 1

 

Design the notification structure informing about the situation: 1

 

Implementation the feature to receive the notification in **mysimbdp-streamingestmanager**:0.75

 

2.75

No explanation of what streamingestmonitor is doing with the report and why.

 

Part 3 (weighted factor=1, max 5 points):

4.5

 

Point 3.1.

 

Present an architecture for the logging and monitoring of both batch and near-realtime ingestion features:

 

Explain the architecture:

 

1

 

Point 3.2:

 

Explain choices/examples of different sinks: 0.5

 

Explain recommendations to the tenants: 0.5

 

1

 

Point 3.3:

 

Explain assumed protections for tenants (encryption of files done by tenants): 0.5

 

Provide recommendations for tenants: 0.5

 

1

 

Point 3.4:

 

Explain features for detecting quality of data: 0.5

 

Explain the design changes: 0.5

 

1

 

Point 3.5:

 

Explain the implication of types of data and workloads: 0.5

 

Explain the extension: 0.5

 

0.5

 

Load balancing with information register by clientbatchingestapp is not a suitable choice since CPU and memory usage have to be profiled and cannot be determined by the program itself, tenants will have to decide how much resource to use and request it.

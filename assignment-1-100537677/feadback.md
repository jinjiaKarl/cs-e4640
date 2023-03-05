This grade is provisional. Why: we need to cross-check all assignments and maybe a face-to-face question to finalize the grade. We also do check the assignments w.r.t. the rule after releasing this grade. In principle, the final grade will be fixed at the end of the course. If you have any feedback, you can send it.



----------------



Overall Grade:  22



Overall comments: Great work and very complete work, however some misunderstanding on the design, data-ingest component is intended for batch and daas component is intended for steaming.



Issues in references/reuse of existing works:



Requests for face-to-face explanation: Yes. Demonstrate good work.



-----------------

Part 1 (max 10 points): 



1.1 choice of application domain and types of data, big data workload situations: 2



1.2 interactions/architecture and third parties: 1

When batching processing from file, sending data row by row as kafka messages is not necessary for batch data-ingest, and the streaming part should be in daas not data-ingest, you mixed up both in data-ingest.



1.3 cluster/no single-point-of-failure configuration: 2



1.4 data replication/redundancy configuration/deployment: 2



1.5 scaling for multi-tenants for mysimbdp (pay attention to the dependencies among components in the design): 1

No scale for mysimbdp-coredms which mysimbdp-dataingest will inject into.



Part 2 (max 10 points): 



2.1 data/schema/structure: 2



2.2 data partition/sharding strategies implementation and explanation: 2



2.3 data ingestion, atomic data element and possible consistency options:2

 

2.4 performance test/discussion (changes of concurrent clients and nodes): 2



2.5 issues observed, changes for solving performance/failure problems: 

2

Part 3 (max 5 points): 



3.1 types of metadata, example of how to find a dataset 1



3.2 service information schema: 0

No schema example was given



3.3 integration of service discovery features: 1



3.4 data ingestion and daas: 1



3.5 pros and cons of deployment examples 1


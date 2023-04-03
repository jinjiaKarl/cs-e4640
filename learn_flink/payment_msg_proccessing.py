################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
from pyflink.table import StreamTableEnvironment, DataTypes, EnvironmentSettings, TableDescriptor, Schema, FormatDescriptor
from pyflink.table.expressions import call, col
from pyflink.table.udf import udf



provinces = ("Beijing", "Shanghai", "Hangzhou", "Shenzhen", "Jiangxi", "Chongqing", "Xizang")


@udf(input_types=[DataTypes.STRING()], result_type=DataTypes.STRING())
def province_id_to_name(id):
    return provinces[id]


def log_processing():
    env = StreamExecutionEnvironment.get_execution_environment()
    t_env = StreamTableEnvironment.create(stream_execution_environment=env)
    t_env.get_config().get_configuration().set_boolean("python.fn-execution.memory.managed", True)

    create_kafka_source_ddl = """
            CREATE TABLE payment_msg(
                createTime VARCHAR,
                orderId BIGINT,
                payAmount DOUBLE,
                payPlatform INT,
                provinceId INT
            ) WITH (
              'connector' = 'kafka',
              'topic' = 'payment_msg',
              'properties.bootstrap.servers' = 'kafka:9092',
              'properties.group.id' = 'test_3',
              'scan.startup.mode' = 'latest-offset',
              'format' = 'json'
            )
            """
    

    t_env.create_temporary_table(
        'sink',
        TableDescriptor.for_connector('filesystem')
            .schema(Schema.new_builder()
                    .column('province', DataTypes.STRING())
                    .column('pay_amount', DataTypes.DOUBLE())
                    .build())
            .option('path', "/tmp/output")
            .format(FormatDescriptor.for_format('canal-json')
                    .build())
            .build())

    t_env.execute_sql(create_kafka_source_ddl) # create a temporary table
    t_env.register_function('province_id_to_name', province_id_to_name)

    table = t_env.from_path("payment_msg") \
        .select(call('province_id_to_name', col('provinceId')).alias("province"), col('payAmount')) \
        .group_by(col('province')) \
        .select(col('province'), call('sum', col('payAmount').alias("pay_amount"))) 
    

    table.execute_insert("sink").wait()

if __name__ == '__main__':
    log_processing()
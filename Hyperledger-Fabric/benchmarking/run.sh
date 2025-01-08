export CALIPER_BENCHCONFIG=benchmarks/scenario/simple/chitfund/config.yaml
export CALIPER_NETWORKCONFIG=networks/fabric/v2.1/network-config_2.1.yaml
  
caliper  launch manager  --caliper-fabric-gateway-enabled --calper-flow-only-test --caliper-fabric-gateway-discovery=false 
#caliper  launch manager  --caliper-fabric-gateway-enabled --calper-flow-only-test --caliper-fabric-gateway-discovery=false
#caliper launch manager --caliper-bind-sut fabric:1.4 --caliper-bind-cwd
#npx caliper bind --caliper-bind-sut fabric:2.1

#npx caliper launch manager --caliper-workspace . --caliper-benchconfig benchmarks/scenario/simple/fabcar/config.yaml --caliper-networkconfig networks/fabric/v2.1/network-config_2.1.yaml --caliper-flow-only-test --caliper-fabric-gateway-enabled

#caliper  launch manager --caliper-workspace . --caliper-benchconfig benchmarks/scenario/simple/fabcar/config.yaml --caliper-networkconfig networks/fabric/v2.1/network-config_2.1.yaml --caliper-fabric-gateway-enabled --calper-flow-only-test --caliper-fabric-gateway-discovery=false



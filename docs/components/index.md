# Components

TyPSA provides Python classes for defining components of different types ([`Bus`](bus.md), [`Load`](load.md), etc.) with their input data.

Your IDE's type checking will verify that the correct data types are being provided while you develop your code. When you run your code, [Pydantic](https://docs.pydantic.dev/latest/) validation ensures that your data inputs are sensible.

Some types of component have multiple component classes, each of which inherits shared attributes from a parent class. For example, the [generator](generator.md) component type has [`Generator`](generator.md#components.generator.Generator), [`ExtendableGenerator`](generator.md#components.generator.ExtendableGenerator), and [`CommittableGenerator`](generator.md#components.generator.CommittableGenerator) classes, all of which inherit from [`BaseGenerator`](generator.md#components.generator.BaseGenerator).

## Component Results

Most component types have a static optimization results class, a dynamic optimization results class, and dynamic (non-)linear simulation results classes. However, there are exceptions. For example, the [`GeneratorOptimizationDynamicResults`](generator.md#components.generator.GeneratorOptimizationDynamicResults) class applies to all generators and can be accessed via property [`OptimizationDynamicResults.of_all_generators`](../network_results.md#results.OptimizationDynamicResults.of_all_generators), but another dynamic results class, [`CommittableGeneratorOptimizationDynamicResults`](generator.md#components.generator.CommittableGeneratorOptimizationDynamicResults), applies only to [`CommittableGenerator`](generator.md#components.generator.CommittableGenerator)s and can only be accessed via property [`OptimizationDynamicResults.committable_generators`](../network_results.md#results.OptimizationDynamicResults.committable_generators).

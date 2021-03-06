from carbon.instrumentation import increment
from carbon.aggregator.rules import RuleManager
from carbon.aggregator.buffers import BufferManager
from carbon.rewrite import RewriteRuleManager
from carbon import events


def process(metric, datapoint):
  increment('datapointsReceived')

  for rule in RewriteRuleManager.preRules:
    metric = rule.apply(metric)

  for rule in RuleManager.rules:
    aggregate_metric = rule.get_aggregate_metric(metric)

    if aggregate_metric is None:
      continue

    buffer = BufferManager.get_buffer(aggregate_metric)

    if not buffer.configured:
      buffer.configure_aggregation(rule.frequency, rule.aggregation_func)

    buffer.input(datapoint)

  for rule in RewriteRuleManager.postRules:
    metric = rule.apply(metric)

  events.metricGenerated(metric, datapoint)

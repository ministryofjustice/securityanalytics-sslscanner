output "notifier" {
  value = aws_sns_topic.detected_ports.arn
}
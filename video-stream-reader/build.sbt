
scalaVersion := "2.13.14"

name := "video-stream-reader"
organization := "com.kgmcquate"
version := "0.1.0"

val sparkVersion = "3.5.2"
val awsSdkVersion = "2.25.31"

mainClass := Some("com.kgmcquate.video.livestream.reader.Main")

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql-kafka-0-10" % sparkVersion,
  "org.apache.spark" %% "spark-streaming-kafka-0-10" % sparkVersion,
  "com.kgmcquate" %% "spark-livestream-reader" % "0.2.0",
  "io.spray" %%  "spray-json" % "1.3.6",
  "software.amazon.awssdk" % "secretsmanager" % awsSdkVersion,
  "software.amazon.awssdk" % "auth" % awsSdkVersion,
  "org.scalatest" %% "scalatest" % "3.2.16" % Test
)

import sbtassembly.AssemblyPlugin.autoImport.*

assembly / assemblyMergeStrategy := {
//  case PathList("META-INF", "io.netty.versions.properties") => MergeStrategy.concat
//  case PathList("META-INF", "versions", "9", "module-info.class") => MergeStrategy.discard
  case x => MergeStrategy.first // Custom default strategy
}

assembly / assemblyJarName  := "video-stream-reader.jar"

githubOwner := "kgmcquate"
githubRepository := "spark-livestream-reader"

githubTokenSource := TokenSource.Environment("GITHUB_TOKEN") || TokenSource.GitConfig("github.token")

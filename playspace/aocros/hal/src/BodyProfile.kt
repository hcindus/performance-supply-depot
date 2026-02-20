/**n * HAL Abstraction Layer for AOCROSn * Port body_profile_schema.json to Kotlinn */
package com.aocros.hal

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class BodyProfile(
    val bodyType: String,
    val version: String,
    val calibratedAt: String,
    val hardware: HardwareSpec,
    val joints: Map<String, JointSpec>,
    val gait: GaitParams? = null,
    val safety: SafetySpec,
    val expressions: Map<String, ExpressionSpec>? = null,
    val network: NetworkSpec? = null
)

@Serializable
data class HardwareSpec(
    val serialNumber: String,
    val firmwareVersion: String,
    val servoCount: Int = 0,
    val sensorCount: Int = 0,
    val hasVision: Boolean = false,
    val hasAudio: Boolean = false,
    val hasLocomotion: Boolean = false
)

@Serializable
data class JointSpec(
    val type: String,  // "servo", "continuous", "prismatic"
    val current: Double,
    val min: Double,
    val max: Double,
    val center: Double,
    val inverted: Boolean = false,
    val pulseMin: Int? = null,
    val pulseMax: Int? = null,
    val gpio: Int? = null
)

@Serializable
data class GaitParams(
    val stepHeight: Double? = null,
    val stepLength: Double? = null,
    val stanceWidth: Double? = null,
    val balanceKp: Double? = null,
    val balanceKi: Double? = null,
    val balanceKd: Double? = null
)

@Serializable
data class SafetySpec(
    val emergencyStopPin: Int,
    val emergencyStopActiveLow: Boolean = true,
    val maxJointSpeed: Double,
    val maxJointTorque: Double? = null,
    val workspaceBounds: Bounds? = null
)

@Serializable
data class Bounds(
    val xMin: Double,
    val xMax: Double,
    val yMin: Double,
    val yMax: Double,
    val zMin: Double,
    val zMax: Double
)

@Serializable
data class ExpressionSpec(
    val ledPattern: String?,
    val ledColor: String?,
    val servoPose: Map<String, Double>? = null,
    val duration: Double? = 1.0
)

@Serializable
data class NetworkSpec(
    val endpoint: String,
    val protocol: String,  // "http", "ros2", "websockets", "serial"
    val authToken: String? = null,
    val lastSeen: String? = null
)

object BodyProfileParser {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }
    
    fun parse(jsonString: String): BodyProfile {
        return json.decodeFromString(BodyProfile.serializer(), jsonString)
    }
    
    fun serialize(profile: BodyProfile): String {
        return json.encodeToString(BodyProfile.serializer(), profile)
    }
}

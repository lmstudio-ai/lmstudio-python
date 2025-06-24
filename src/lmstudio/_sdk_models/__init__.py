from __future__ import annotations
from typing import Annotated, Any, ClassVar, Literal, Mapping, Sequence, TypedDict
from msgspec import Meta, field
from typing_extensions import NotRequired
from ..schemas import LMStudioStruct

LogLevel = Literal["debug", "info", "warn", "error"]
AllowableEnvVarKeys = Literal["HSA_OVERRIDE_GFX_VERSION"]
AllowableEnvVars = Mapping[str, str] | None
ArtifactType = Literal["plugin", "preset", "model"]
ArtifactDependencyPurpose = Literal["baseModel", "draftModel", "custom"]
ModelKey = Annotated[str, Meta(min_length=1)]

__all__ = [
    "Accelerator",
    "AcceleratorDict",
    "ArtifactArtifactDependency",
    "ArtifactArtifactDependencyDict",
    "ArtifactDependencyBase",
    "ArtifactDependencyBaseDict",
    "ArtifactDownloadPlan",
    "ArtifactDownloadPlanDict",
    "ArtifactDownloadPlanModelInfo",
    "ArtifactDownloadPlanModelInfoDict",
    "ArtifactDownloadPlanNodeArtifact",
    "ArtifactDownloadPlanNodeArtifactDict",
    "ArtifactDownloadPlanNodeModel",
    "ArtifactDownloadPlanNodeModelDict",
    "ArtifactManifestBase",
    "ArtifactManifestBaseDict",
    "ArtifactModelDependency",
    "ArtifactModelDependencyDict",
    "AssistantResponse",
    "AssistantResponseDict",
    "AvailablePresetsSampleItem",
    "AvailablePresetsSampleItemDict",
    "BackendNotification",
    "BackendNotificationDict",
    "BlockLocationAfterId",
    "BlockLocationAfterIdDict",
    "BlockLocationBeforeId",
    "BlockLocationBeforeIdDict",
    "ChatHistoryData",
    "ChatHistoryDataDict",
    "CitationSource",
    "CitationSourceDict",
    "Config",
    "ConfigDict",
    "ContentBlockStyleCustomLabel",
    "ContentBlockStyleCustomLabelDict",
    "ContentBlockStyleDefault",
    "ContentBlockStyleDefaultDict",
    "ContentBlockStyleThinking",
    "ContentBlockStyleThinkingDict",
    "DiagnosticsChannelStreamLogsToClientPacketLog",
    "DiagnosticsChannelStreamLogsToClientPacketLogDict",
    "DiagnosticsChannelStreamLogsToServerPacketStop",
    "DiagnosticsChannelStreamLogsToServerPacketStopDict",
    "DiagnosticsLogEvent",
    "DiagnosticsLogEventDataLlmPredictionInput",
    "DiagnosticsLogEventDataLlmPredictionInputDict",
    "DiagnosticsLogEventDict",
    "DocumentParsingLibraryIdentifier",
    "DocumentParsingLibraryIdentifierDict",
    "DocumentParsingOpts",
    "DocumentParsingOptsDict",
    "DownloadModelChannelRequest",
    "DownloadModelChannelRequestDict",
    "DownloadProgressUpdate",
    "DownloadProgressUpdateDict",
    "EmbeddingChannelGetOrLoadCreationParameter",
    "EmbeddingChannelGetOrLoadCreationParameterDict",
    "EmbeddingChannelGetOrLoadToClientPacketAlreadyLoaded",
    "EmbeddingChannelGetOrLoadToClientPacketAlreadyLoadedDict",
    "EmbeddingChannelGetOrLoadToClientPacketLoadProgress",
    "EmbeddingChannelGetOrLoadToClientPacketLoadProgressDict",
    "EmbeddingChannelGetOrLoadToClientPacketLoadSuccess",
    "EmbeddingChannelGetOrLoadToClientPacketLoadSuccessDict",
    "EmbeddingChannelGetOrLoadToClientPacketStartLoading",
    "EmbeddingChannelGetOrLoadToClientPacketStartLoadingDict",
    "EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModel",
    "EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict",
    "EmbeddingChannelGetOrLoadToServerPacketCancel",
    "EmbeddingChannelGetOrLoadToServerPacketCancelDict",
    "EmbeddingChannelLoadModelCreationParameter",
    "EmbeddingChannelLoadModelCreationParameterDict",
    "EmbeddingChannelLoadModelToClientPacketProgress",
    "EmbeddingChannelLoadModelToClientPacketProgressDict",
    "EmbeddingChannelLoadModelToClientPacketResolved",
    "EmbeddingChannelLoadModelToClientPacketResolvedDict",
    "EmbeddingChannelLoadModelToClientPacketSuccess",
    "EmbeddingChannelLoadModelToClientPacketSuccessDict",
    "EmbeddingChannelLoadModelToServerPacketCancel",
    "EmbeddingChannelLoadModelToServerPacketCancelDict",
    "EmbeddingLoadModelConfig",
    "EmbeddingLoadModelConfigDict",
    "EmbeddingModelAdditionalInfo",
    "EmbeddingModelAdditionalInfoDict",
    "EmbeddingModelInfo",
    "EmbeddingModelInfoDict",
    "EmbeddingModelInstanceAdditionalInfo",
    "EmbeddingModelInstanceAdditionalInfoDict",
    "EmbeddingModelInstanceInfo",
    "EmbeddingModelInstanceInfoDict",
    "EmbeddingRpcCountTokensParameter",
    "EmbeddingRpcCountTokensParameterDict",
    "EmbeddingRpcCountTokensReturns",
    "EmbeddingRpcCountTokensReturnsDict",
    "EmbeddingRpcEmbedStringParameter",
    "EmbeddingRpcEmbedStringParameterDict",
    "EmbeddingRpcEmbedStringReturns",
    "EmbeddingRpcEmbedStringReturnsDict",
    "EmbeddingRpcGetLoadConfigParameter",
    "EmbeddingRpcGetLoadConfigParameterDict",
    "EmbeddingRpcGetLoadConfigReturns",
    "EmbeddingRpcGetLoadConfigReturnsDict",
    "EmbeddingRpcGetModelInfoParameter",
    "EmbeddingRpcGetModelInfoParameterDict",
    "EmbeddingRpcTokenizeParameter",
    "EmbeddingRpcTokenizeParameterDict",
    "EmbeddingRpcTokenizeReturns",
    "EmbeddingRpcTokenizeReturnsDict",
    "EmbeddingRpcUnloadModelParameter",
    "EmbeddingRpcUnloadModelParameterDict",
    "ErrorDisplayDataGenericDomainMismatch",
    "ErrorDisplayDataGenericDomainMismatchDict",
    "ErrorDisplayDataGenericEngineDoesNotSupportFeature",
    "ErrorDisplayDataGenericEngineDoesNotSupportFeatureDict",
    "ErrorDisplayDataGenericIdentifierNotFound",
    "ErrorDisplayDataGenericIdentifierNotFoundDict",
    "ErrorDisplayDataGenericNoModelMatchingQuery",
    "ErrorDisplayDataGenericNoModelMatchingQueryDict",
    "ErrorDisplayDataGenericPathNotFound",
    "ErrorDisplayDataGenericPathNotFoundDict",
    "ErrorDisplayDataGenericPresetNotFound",
    "ErrorDisplayDataGenericPresetNotFoundDict",
    "ErrorDisplayDataGenericSpecificModelUnloaded",
    "ErrorDisplayDataGenericSpecificModelUnloadedDict",
    "FileHandle",
    "FileHandleDict",
    "FilesChannelParseDocumentCreationParameter",
    "FilesChannelParseDocumentCreationParameterDict",
    "FilesChannelParseDocumentToClientPacketParserLoaded",
    "FilesChannelParseDocumentToClientPacketParserLoadedDict",
    "FilesChannelParseDocumentToClientPacketProgress",
    "FilesChannelParseDocumentToClientPacketProgressDict",
    "FilesChannelParseDocumentToClientPacketResult",
    "FilesChannelParseDocumentToClientPacketResultDict",
    "FilesChannelParseDocumentToServerPacketCancel",
    "FilesChannelParseDocumentToServerPacketCancelDict",
    "FilesChannelRetrieveCreationParameter",
    "FilesChannelRetrieveCreationParameterDict",
    "FilesChannelRetrieveToClientPacketOnFileProcessList",
    "FilesChannelRetrieveToClientPacketOnFileProcessListDict",
    "FilesChannelRetrieveToClientPacketOnFileProcessingEnd",
    "FilesChannelRetrieveToClientPacketOnFileProcessingEndDict",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStart",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStartDict",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStepEnd",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStepEndDict",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStepProgress",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStepProgressDict",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStepStart",
    "FilesChannelRetrieveToClientPacketOnFileProcessingStepStartDict",
    "FilesChannelRetrieveToClientPacketOnSearchingEnd",
    "FilesChannelRetrieveToClientPacketOnSearchingEndDict",
    "FilesChannelRetrieveToClientPacketOnSearchingStart",
    "FilesChannelRetrieveToClientPacketOnSearchingStartDict",
    "FilesChannelRetrieveToClientPacketResult",
    "FilesChannelRetrieveToClientPacketResultDict",
    "FilesChannelRetrieveToServerPacketStop",
    "FilesChannelRetrieveToServerPacketStopDict",
    "FilesRpcGetDocumentParsingLibraryParameter",
    "FilesRpcGetDocumentParsingLibraryParameterDict",
    "FilesRpcGetDocumentParsingLibraryReturns",
    "FilesRpcGetDocumentParsingLibraryReturnsDict",
    "FilesRpcGetLocalFileAbsolutePathParameter",
    "FilesRpcGetLocalFileAbsolutePathParameterDict",
    "FilesRpcGetLocalFileAbsolutePathReturns",
    "FilesRpcGetLocalFileAbsolutePathReturnsDict",
    "FilesRpcUploadFileBase64Parameter",
    "FilesRpcUploadFileBase64ParameterDict",
    "FilesRpcUploadFileBase64Returns",
    "FilesRpcUploadFileBase64ReturnsDict",
    "Function",
    "FunctionDict",
    "GetModelOpts",
    "GetModelOptsDict",
    "GpuSetting",
    "GpuSettingDict",
    "GpuSplitConfig",
    "GpuSplitConfigDict",
    "HuggingFaceModelDownloadSource",
    "HuggingFaceModelDownloadSourceDict",
    "InternalRetrievalResult",
    "InternalRetrievalResultDict",
    "InternalRetrievalResultEntry",
    "InternalRetrievalResultEntryDict",
    "KvConfig",
    "KvConfigDict",
    "KvConfigField",
    "KvConfigFieldDependency",
    "KvConfigFieldDependencyConditionEquals",
    "KvConfigFieldDependencyConditionEqualsDict",
    "KvConfigFieldDependencyConditionNotEquals",
    "KvConfigFieldDependencyConditionNotEqualsDict",
    "KvConfigFieldDependencyDict",
    "KvConfigFieldDict",
    "KvConfigSchematicsDeserializationError",
    "KvConfigSchematicsDeserializationErrorDict",
    "KvConfigStack",
    "KvConfigStackDict",
    "KvConfigStackLayer",
    "KvConfigStackLayerDict",
    "LlmAdditionalInfo",
    "LlmAdditionalInfoDict",
    "LlmApplyPromptTemplateOpts",
    "LlmApplyPromptTemplateOptsDict",
    "LlmChannelGenerateWithGeneratorCreationParameter",
    "LlmChannelGenerateWithGeneratorCreationParameterDict",
    "LlmChannelGenerateWithGeneratorToClientPacketFragment",
    "LlmChannelGenerateWithGeneratorToClientPacketFragmentDict",
    "LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgress",
    "LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgressDict",
    "LlmChannelGenerateWithGeneratorToClientPacketSuccess",
    "LlmChannelGenerateWithGeneratorToClientPacketSuccessDict",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGenerated",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGeneratedDict",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEnd",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEndDict",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailed",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailedDict",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceived",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceivedDict",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStart",
    "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStartDict",
    "LlmChannelGenerateWithGeneratorToServerPacketCancel",
    "LlmChannelGenerateWithGeneratorToServerPacketCancelDict",
    "LlmChannelGetOrLoadCreationParameter",
    "LlmChannelGetOrLoadCreationParameterDict",
    "LlmChannelGetOrLoadToClientPacketAlreadyLoaded",
    "LlmChannelGetOrLoadToClientPacketAlreadyLoadedDict",
    "LlmChannelGetOrLoadToClientPacketLoadProgress",
    "LlmChannelGetOrLoadToClientPacketLoadProgressDict",
    "LlmChannelGetOrLoadToClientPacketLoadSuccess",
    "LlmChannelGetOrLoadToClientPacketLoadSuccessDict",
    "LlmChannelGetOrLoadToClientPacketStartLoading",
    "LlmChannelGetOrLoadToClientPacketStartLoadingDict",
    "LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModel",
    "LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict",
    "LlmChannelGetOrLoadToServerPacketCancel",
    "LlmChannelGetOrLoadToServerPacketCancelDict",
    "LlmChannelLoadModelCreationParameter",
    "LlmChannelLoadModelCreationParameterDict",
    "LlmChannelLoadModelToClientPacketProgress",
    "LlmChannelLoadModelToClientPacketProgressDict",
    "LlmChannelLoadModelToClientPacketResolved",
    "LlmChannelLoadModelToClientPacketResolvedDict",
    "LlmChannelLoadModelToClientPacketSuccess",
    "LlmChannelLoadModelToClientPacketSuccessDict",
    "LlmChannelLoadModelToServerPacketCancel",
    "LlmChannelLoadModelToServerPacketCancelDict",
    "LlmChannelPredictToClientPacketFragment",
    "LlmChannelPredictToClientPacketFragmentDict",
    "LlmChannelPredictToClientPacketPromptProcessingProgress",
    "LlmChannelPredictToClientPacketPromptProcessingProgressDict",
    "LlmChannelPredictToClientPacketSuccess",
    "LlmChannelPredictToClientPacketSuccessDict",
    "LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGenerated",
    "LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGeneratedDict",
    "LlmChannelPredictToClientPacketToolCallGenerationEnd",
    "LlmChannelPredictToClientPacketToolCallGenerationEndDict",
    "LlmChannelPredictToClientPacketToolCallGenerationFailed",
    "LlmChannelPredictToClientPacketToolCallGenerationFailedDict",
    "LlmChannelPredictToClientPacketToolCallGenerationNameReceived",
    "LlmChannelPredictToClientPacketToolCallGenerationNameReceivedDict",
    "LlmChannelPredictToClientPacketToolCallGenerationStart",
    "LlmChannelPredictToClientPacketToolCallGenerationStartDict",
    "LlmChannelPredictToServerPacketCancel",
    "LlmChannelPredictToServerPacketCancelDict",
    "LlmContextReferenceJsonFile",
    "LlmContextReferenceJsonFileDict",
    "LlmContextReferenceYamlFile",
    "LlmContextReferenceYamlFileDict",
    "LlmGenInfo",
    "LlmGenInfoDict",
    "LlmInfo",
    "LlmInfoDict",
    "LlmInstanceAdditionalInfo",
    "LlmInstanceAdditionalInfoDict",
    "LlmInstanceInfo",
    "LlmInstanceInfoDict",
    "LlmJinjaPromptTemplate",
    "LlmJinjaPromptTemplateDict",
    "LlmLlamaMirostatSamplingConfig",
    "LlmLlamaMirostatSamplingConfigDict",
    "LlmLoadModelConfig",
    "LlmLoadModelConfigDict",
    "LlmManualPromptTemplate",
    "LlmManualPromptTemplateDict",
    "LlmMlxKvCacheQuantization",
    "LlmMlxKvCacheQuantizationDict",
    "LlmPredictionConfig",
    "LlmPredictionConfigDict",
    "LlmPredictionConfigInput",
    "LlmPredictionConfigInputDict",
    "LlmPredictionFragment",
    "LlmPredictionFragmentDict",
    "LlmPredictionFragmentInputOpts",
    "LlmPredictionFragmentInputOptsDict",
    "LlmPredictionStats",
    "LlmPredictionStatsDict",
    "LlmPromptTemplate",
    "LlmPromptTemplateDict",
    "LlmReasoningParsing",
    "LlmReasoningParsingDict",
    "LlmRpcApplyPromptTemplateParameter",
    "LlmRpcApplyPromptTemplateParameterDict",
    "LlmRpcApplyPromptTemplateReturns",
    "LlmRpcApplyPromptTemplateReturnsDict",
    "LlmRpcCountTokensParameter",
    "LlmRpcCountTokensParameterDict",
    "LlmRpcCountTokensReturns",
    "LlmRpcCountTokensReturnsDict",
    "LlmRpcGetLoadConfigParameter",
    "LlmRpcGetLoadConfigParameterDict",
    "LlmRpcGetLoadConfigReturns",
    "LlmRpcGetLoadConfigReturnsDict",
    "LlmRpcGetModelInfoParameter",
    "LlmRpcGetModelInfoParameterDict",
    "LlmRpcPreloadDraftModelParameter",
    "LlmRpcPreloadDraftModelParameterDict",
    "LlmRpcTokenizeParameter",
    "LlmRpcTokenizeParameterDict",
    "LlmRpcTokenizeReturns",
    "LlmRpcTokenizeReturnsDict",
    "LlmRpcUnloadModelParameter",
    "LlmRpcUnloadModelParameterDict",
    "LlmStructuredPredictionSetting",
    "LlmStructuredPredictionSettingDict",
    "LlmToolFunction",
    "LlmToolFunctionDict",
    "LlmToolParametersObject",
    "LlmToolParametersObjectDict",
    "LlmToolUseSettingNone",
    "LlmToolUseSettingNoneDict",
    "LlmToolUseSettingToolArray",
    "LlmToolUseSettingToolArrayDict",
    "LocalArtifactFileEntry",
    "LocalArtifactFileEntryDict",
    "LocalArtifactFileList",
    "LocalArtifactFileListDict",
    "Logprob",
    "LogprobDict",
    "Model",
    "ModelDict",
    "ModelInfoBase",
    "ModelInfoBaseDict",
    "ModelInstanceInfoBase",
    "ModelInstanceInfoBaseDict",
    "ModelManifest",
    "ModelManifestDict",
    "ModelQuery",
    "ModelQueryDict",
    "ModelSearchOpts",
    "ModelSearchOptsDict",
    "ModelSearchResultDownloadOptionData",
    "ModelSearchResultDownloadOptionDataDict",
    "ModelSearchResultEntryData",
    "ModelSearchResultEntryDataDict",
    "ModelSearchResultIdentifierCatalog",
    "ModelSearchResultIdentifierCatalogDict",
    "ModelSearchResultIdentifierHf",
    "ModelSearchResultIdentifierHfDict",
    "ModelSpecifierInstanceReference",
    "ModelSpecifierInstanceReferenceDict",
    "ModelSpecifierQuery",
    "ModelSpecifierQueryDict",
    "ParsedFileIdentifierBase64",
    "ParsedFileIdentifierBase64Dict",
    "ParsedFileIdentifierLocal",
    "ParsedFileIdentifierLocalDict",
    "PluginManifest",
    "PluginManifestDict",
    "PluginsChannelRegisterDevelopmentPluginCreationParameter",
    "PluginsChannelRegisterDevelopmentPluginCreationParameterDict",
    "PluginsChannelRegisterDevelopmentPluginToClientPacketReady",
    "PluginsChannelRegisterDevelopmentPluginToClientPacketReadyDict",
    "PluginsChannelRegisterDevelopmentPluginToServerPacketEnd",
    "PluginsChannelRegisterDevelopmentPluginToServerPacketEndDict",
    "PluginsChannelSetGeneratorToClientPacketAbort",
    "PluginsChannelSetGeneratorToClientPacketAbortDict",
    "PluginsChannelSetGeneratorToClientPacketGenerate",
    "PluginsChannelSetGeneratorToClientPacketGenerateDict",
    "PluginsChannelSetGeneratorToServerPacketAborted",
    "PluginsChannelSetGeneratorToServerPacketAbortedDict",
    "PluginsChannelSetGeneratorToServerPacketComplete",
    "PluginsChannelSetGeneratorToServerPacketCompleteDict",
    "PluginsChannelSetGeneratorToServerPacketError",
    "PluginsChannelSetGeneratorToServerPacketErrorDict",
    "PluginsChannelSetGeneratorToServerPacketFragmentGenerated",
    "PluginsChannelSetGeneratorToServerPacketFragmentGeneratedDict",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGenerated",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGeneratedDict",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationEnded",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationEndedDict",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailed",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailedDict",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceived",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceivedDict",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationStarted",
    "PluginsChannelSetGeneratorToServerPacketToolCallGenerationStartedDict",
    "PluginsChannelSetPredictionLoopHandlerToClientPacketAbort",
    "PluginsChannelSetPredictionLoopHandlerToClientPacketAbortDict",
    "PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoop",
    "PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoopDict",
    "PluginsChannelSetPredictionLoopHandlerToServerPacketAborted",
    "PluginsChannelSetPredictionLoopHandlerToServerPacketAbortedDict",
    "PluginsChannelSetPredictionLoopHandlerToServerPacketComplete",
    "PluginsChannelSetPredictionLoopHandlerToServerPacketCompleteDict",
    "PluginsChannelSetPredictionLoopHandlerToServerPacketError",
    "PluginsChannelSetPredictionLoopHandlerToServerPacketErrorDict",
    "PluginsChannelSetPreprocessorToClientPacketAbort",
    "PluginsChannelSetPreprocessorToClientPacketAbortDict",
    "PluginsChannelSetPreprocessorToClientPacketPreprocess",
    "PluginsChannelSetPreprocessorToClientPacketPreprocessDict",
    "PluginsChannelSetPreprocessorToServerPacketAborted",
    "PluginsChannelSetPreprocessorToServerPacketAbortedDict",
    "PluginsChannelSetPreprocessorToServerPacketComplete",
    "PluginsChannelSetPreprocessorToServerPacketCompleteDict",
    "PluginsChannelSetPreprocessorToServerPacketError",
    "PluginsChannelSetPreprocessorToServerPacketErrorDict",
    "PluginsChannelSetToolsProviderToClientPacketAbortToolCall",
    "PluginsChannelSetToolsProviderToClientPacketAbortToolCallDict",
    "PluginsChannelSetToolsProviderToClientPacketCallTool",
    "PluginsChannelSetToolsProviderToClientPacketCallToolDict",
    "PluginsChannelSetToolsProviderToClientPacketDiscardSession",
    "PluginsChannelSetToolsProviderToClientPacketDiscardSessionDict",
    "PluginsChannelSetToolsProviderToClientPacketInitSession",
    "PluginsChannelSetToolsProviderToClientPacketInitSessionDict",
    "PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailed",
    "PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict",
    "PluginsChannelSetToolsProviderToServerPacketSessionInitialized",
    "PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict",
    "PluginsChannelSetToolsProviderToServerPacketToolCallComplete",
    "PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict",
    "PluginsChannelSetToolsProviderToServerPacketToolCallError",
    "PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict",
    "PluginsChannelSetToolsProviderToServerPacketToolCallStatus",
    "PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict",
    "PluginsChannelSetToolsProviderToServerPacketToolCallWarn",
    "PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict",
    "PluginsRpcProcessingGetOrLoadModelParameter",
    "PluginsRpcProcessingGetOrLoadModelParameterDict",
    "PluginsRpcProcessingGetOrLoadModelReturns",
    "PluginsRpcProcessingGetOrLoadModelReturnsDict",
    "PluginsRpcProcessingHandleRequestParameter",
    "PluginsRpcProcessingHandleRequestParameterDict",
    "PluginsRpcProcessingHandleRequestReturns",
    "PluginsRpcProcessingHandleRequestReturnsDict",
    "PluginsRpcProcessingHandleUpdateParameter",
    "PluginsRpcProcessingHandleUpdateParameterDict",
    "PluginsRpcProcessingHasStatusParameter",
    "PluginsRpcProcessingHasStatusParameterDict",
    "PluginsRpcProcessingNeedsNamingParameter",
    "PluginsRpcProcessingNeedsNamingParameterDict",
    "PluginsRpcProcessingPullHistoryParameter",
    "PluginsRpcProcessingPullHistoryParameterDict",
    "PluginsRpcProcessingPullHistoryReturns",
    "PluginsRpcProcessingPullHistoryReturnsDict",
    "PluginsRpcProcessingSetSenderNameParameter",
    "PluginsRpcProcessingSetSenderNameParameterDict",
    "PluginsRpcProcessingSuggestNameParameter",
    "PluginsRpcProcessingSuggestNameParameterDict",
    "PluginsRpcSetConfigSchematicsParameter",
    "PluginsRpcSetConfigSchematicsParameterDict",
    "PluginsRpcSetGlobalConfigSchematicsParameter",
    "PluginsRpcSetGlobalConfigSchematicsParameterDict",
    "PredictionChannelRequest",
    "PredictionChannelRequestDict",
    "PresetManifest",
    "PresetManifestDict",
    "ProcessingRequestConfirmToolCall",
    "ProcessingRequestConfirmToolCallDict",
    "ProcessingRequestResponseConfirmToolCall",
    "ProcessingRequestResponseConfirmToolCallDict",
    "ProcessingRequestResponseConfirmToolCallResultAllow",
    "ProcessingRequestResponseConfirmToolCallResultAllowDict",
    "ProcessingRequestResponseConfirmToolCallResultDeny",
    "ProcessingRequestResponseConfirmToolCallResultDenyDict",
    "ProcessingRequestResponseTextInput",
    "ProcessingRequestResponseTextInputDict",
    "ProcessingRequestTextInput",
    "ProcessingRequestTextInputDict",
    "ProcessingUpdateCitationBlockCreate",
    "ProcessingUpdateCitationBlockCreateDict",
    "ProcessingUpdateContentBlockAppendText",
    "ProcessingUpdateContentBlockAppendTextDict",
    "ProcessingUpdateContentBlockAppendToolRequest",
    "ProcessingUpdateContentBlockAppendToolRequestDict",
    "ProcessingUpdateContentBlockAppendToolResult",
    "ProcessingUpdateContentBlockAppendToolResultDict",
    "ProcessingUpdateContentBlockAttachGenInfo",
    "ProcessingUpdateContentBlockAttachGenInfoDict",
    "ProcessingUpdateContentBlockCreate",
    "ProcessingUpdateContentBlockCreateDict",
    "ProcessingUpdateContentBlockReplaceText",
    "ProcessingUpdateContentBlockReplaceTextDict",
    "ProcessingUpdateContentBlockReplaceToolRequest",
    "ProcessingUpdateContentBlockReplaceToolRequestDict",
    "ProcessingUpdateContentBlockSetPrefix",
    "ProcessingUpdateContentBlockSetPrefixDict",
    "ProcessingUpdateContentBlockSetStyle",
    "ProcessingUpdateContentBlockSetStyleDict",
    "ProcessingUpdateContentBlockSetSuffix",
    "ProcessingUpdateContentBlockSetSuffixDict",
    "ProcessingUpdateDebugInfoBlockCreate",
    "ProcessingUpdateDebugInfoBlockCreateDict",
    "ProcessingUpdateSetSenderName",
    "ProcessingUpdateSetSenderNameDict",
    "ProcessingUpdateStatusCreate",
    "ProcessingUpdateStatusCreateDict",
    "ProcessingUpdateStatusRemove",
    "ProcessingUpdateStatusRemoveDict",
    "ProcessingUpdateStatusUpdate",
    "ProcessingUpdateStatusUpdateDict",
    "ProcessingUpdateToolStatusArgumentFragment",
    "ProcessingUpdateToolStatusArgumentFragmentDict",
    "ProcessingUpdateToolStatusCreate",
    "ProcessingUpdateToolStatusCreateDict",
    "ProcessingUpdateToolStatusUpdate",
    "ProcessingUpdateToolStatusUpdateDict",
    "PseudoDiagnostics",
    "PseudoDiagnosticsChannelStreamLogs",
    "PseudoDiagnosticsChannelStreamLogsDict",
    "PseudoDiagnosticsDict",
    "PseudoEmbedding",
    "PseudoEmbeddingChannelGetOrLoad",
    "PseudoEmbeddingChannelGetOrLoadDict",
    "PseudoEmbeddingChannelLoadModel",
    "PseudoEmbeddingChannelLoadModelDict",
    "PseudoEmbeddingDict",
    "PseudoEmbeddingRpcCountTokens",
    "PseudoEmbeddingRpcCountTokensDict",
    "PseudoEmbeddingRpcEmbedString",
    "PseudoEmbeddingRpcEmbedStringDict",
    "PseudoEmbeddingRpcGetLoadConfig",
    "PseudoEmbeddingRpcGetLoadConfigDict",
    "PseudoEmbeddingRpcGetModelInfo",
    "PseudoEmbeddingRpcGetModelInfoDict",
    "PseudoEmbeddingRpcListLoaded",
    "PseudoEmbeddingRpcListLoadedDict",
    "PseudoEmbeddingRpcTokenize",
    "PseudoEmbeddingRpcTokenizeDict",
    "PseudoEmbeddingRpcUnloadModel",
    "PseudoEmbeddingRpcUnloadModelDict",
    "PseudoFiles",
    "PseudoFilesChannelParseDocument",
    "PseudoFilesChannelParseDocumentDict",
    "PseudoFilesChannelRetrieve",
    "PseudoFilesChannelRetrieveDict",
    "PseudoFilesDict",
    "PseudoFilesRpcGetDocumentParsingLibrary",
    "PseudoFilesRpcGetDocumentParsingLibraryDict",
    "PseudoFilesRpcGetLocalFileAbsolutePath",
    "PseudoFilesRpcGetLocalFileAbsolutePathDict",
    "PseudoFilesRpcUploadFileBase64",
    "PseudoFilesRpcUploadFileBase64Dict",
    "PseudoLlm",
    "PseudoLlmChannelGenerateWithGenerator",
    "PseudoLlmChannelGenerateWithGeneratorDict",
    "PseudoLlmChannelGetOrLoad",
    "PseudoLlmChannelGetOrLoadDict",
    "PseudoLlmChannelLoadModel",
    "PseudoLlmChannelLoadModelDict",
    "PseudoLlmChannelPredict",
    "PseudoLlmChannelPredictDict",
    "PseudoLlmDict",
    "PseudoLlmRpcApplyPromptTemplate",
    "PseudoLlmRpcApplyPromptTemplateDict",
    "PseudoLlmRpcCountTokens",
    "PseudoLlmRpcCountTokensDict",
    "PseudoLlmRpcGetLoadConfig",
    "PseudoLlmRpcGetLoadConfigDict",
    "PseudoLlmRpcGetModelInfo",
    "PseudoLlmRpcGetModelInfoDict",
    "PseudoLlmRpcListLoaded",
    "PseudoLlmRpcListLoadedDict",
    "PseudoLlmRpcPreloadDraftModel",
    "PseudoLlmRpcPreloadDraftModelDict",
    "PseudoLlmRpcTokenize",
    "PseudoLlmRpcTokenizeDict",
    "PseudoLlmRpcUnloadModel",
    "PseudoLlmRpcUnloadModelDict",
    "PseudoPlugins",
    "PseudoPluginsChannelRegisterDevelopmentPlugin",
    "PseudoPluginsChannelRegisterDevelopmentPluginDict",
    "PseudoPluginsChannelSetGenerator",
    "PseudoPluginsChannelSetGeneratorDict",
    "PseudoPluginsChannelSetPredictionLoopHandler",
    "PseudoPluginsChannelSetPredictionLoopHandlerDict",
    "PseudoPluginsChannelSetPreprocessor",
    "PseudoPluginsChannelSetPreprocessorDict",
    "PseudoPluginsChannelSetToolsProvider",
    "PseudoPluginsChannelSetToolsProviderDict",
    "PseudoPluginsDict",
    "PseudoPluginsRpcPluginInitCompleted",
    "PseudoPluginsRpcProcessingGetOrLoadModel",
    "PseudoPluginsRpcProcessingGetOrLoadModelDict",
    "PseudoPluginsRpcProcessingHandleRequest",
    "PseudoPluginsRpcProcessingHandleRequestDict",
    "PseudoPluginsRpcProcessingHandleUpdate",
    "PseudoPluginsRpcProcessingHandleUpdateDict",
    "PseudoPluginsRpcProcessingHasStatus",
    "PseudoPluginsRpcProcessingHasStatusDict",
    "PseudoPluginsRpcProcessingNeedsNaming",
    "PseudoPluginsRpcProcessingNeedsNamingDict",
    "PseudoPluginsRpcProcessingPullHistory",
    "PseudoPluginsRpcProcessingPullHistoryDict",
    "PseudoPluginsRpcProcessingSetSenderName",
    "PseudoPluginsRpcProcessingSetSenderNameDict",
    "PseudoPluginsRpcProcessingSuggestName",
    "PseudoPluginsRpcProcessingSuggestNameDict",
    "PseudoPluginsRpcReindexPlugins",
    "PseudoPluginsRpcSetConfigSchematics",
    "PseudoPluginsRpcSetConfigSchematicsDict",
    "PseudoPluginsRpcSetGlobalConfigSchematics",
    "PseudoPluginsRpcSetGlobalConfigSchematicsDict",
    "PseudoRepository",
    "PseudoRepositoryChannelCreateArtifactDownloadPlan",
    "PseudoRepositoryChannelCreateArtifactDownloadPlanDict",
    "PseudoRepositoryChannelDownloadArtifact",
    "PseudoRepositoryChannelDownloadArtifactDict",
    "PseudoRepositoryChannelDownloadModel",
    "PseudoRepositoryChannelDownloadModelDict",
    "PseudoRepositoryChannelEnsureAuthenticated",
    "PseudoRepositoryChannelEnsureAuthenticatedDict",
    "PseudoRepositoryChannelPushArtifact",
    "PseudoRepositoryChannelPushArtifactDict",
    "PseudoRepositoryDict",
    "PseudoRepositoryRpcGetLocalArtifactFiles",
    "PseudoRepositoryRpcGetLocalArtifactFilesDict",
    "PseudoRepositoryRpcGetModelDownloadOptions",
    "PseudoRepositoryRpcGetModelDownloadOptionsDict",
    "PseudoRepositoryRpcInstallPluginDependencies",
    "PseudoRepositoryRpcInstallPluginDependenciesDict",
    "PseudoRepositoryRpcLoginWithPreAuthenticatedKeys",
    "PseudoRepositoryRpcLoginWithPreAuthenticatedKeysDict",
    "PseudoRepositoryRpcSearchModels",
    "PseudoRepositoryRpcSearchModelsDict",
    "PseudoSystem",
    "PseudoSystemChannelAlive",
    "PseudoSystemDict",
    "PseudoSystemRpcGetExperimentFlags",
    "PseudoSystemRpcGetExperimentFlagsDict",
    "PseudoSystemRpcListDownloadedModels",
    "PseudoSystemRpcListDownloadedModelsDict",
    "PseudoSystemRpcNotify",
    "PseudoSystemRpcNotifyDict",
    "PseudoSystemRpcSetExperimentFlag",
    "PseudoSystemRpcSetExperimentFlagDict",
    "PseudoSystemRpcVersion",
    "PseudoSystemRpcVersionDict",
    "RepositoryChannelCreateArtifactDownloadPlanCreationParameter",
    "RepositoryChannelCreateArtifactDownloadPlanCreationParameterDict",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgress",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgressDict",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReady",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReadyDict",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdated",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdatedDict",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizing",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizingDict",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccess",
    "RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccessDict",
    "RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancel",
    "RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancelDict",
    "RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommit",
    "RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommitDict",
    "RepositoryChannelDownloadArtifactCreationParameter",
    "RepositoryChannelDownloadArtifactCreationParameterDict",
    "RepositoryChannelDownloadArtifactToClientPacketDownloadProgress",
    "RepositoryChannelDownloadArtifactToClientPacketDownloadProgressDict",
    "RepositoryChannelDownloadArtifactToClientPacketStartFinalizing",
    "RepositoryChannelDownloadArtifactToClientPacketStartFinalizingDict",
    "RepositoryChannelDownloadArtifactToClientPacketSuccess",
    "RepositoryChannelDownloadArtifactToClientPacketSuccessDict",
    "RepositoryChannelDownloadArtifactToServerPacketCancel",
    "RepositoryChannelDownloadArtifactToServerPacketCancelDict",
    "RepositoryChannelDownloadModelToClientPacketDownloadProgress",
    "RepositoryChannelDownloadModelToClientPacketDownloadProgressDict",
    "RepositoryChannelDownloadModelToClientPacketStartFinalizing",
    "RepositoryChannelDownloadModelToClientPacketStartFinalizingDict",
    "RepositoryChannelDownloadModelToClientPacketSuccess",
    "RepositoryChannelDownloadModelToClientPacketSuccessDict",
    "RepositoryChannelDownloadModelToServerPacketCancel",
    "RepositoryChannelDownloadModelToServerPacketCancelDict",
    "RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticated",
    "RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticatedDict",
    "RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrl",
    "RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrlDict",
    "RepositoryChannelPushArtifactCreationParameter",
    "RepositoryChannelPushArtifactCreationParameterDict",
    "RepositoryChannelPushArtifactToClientPacketMessage",
    "RepositoryChannelPushArtifactToClientPacketMessageDict",
    "RepositoryRpcGetLocalArtifactFilesParameter",
    "RepositoryRpcGetLocalArtifactFilesParameterDict",
    "RepositoryRpcGetLocalArtifactFilesReturns",
    "RepositoryRpcGetLocalArtifactFilesReturnsDict",
    "RepositoryRpcGetModelDownloadOptionsParameter",
    "RepositoryRpcGetModelDownloadOptionsParameterDict",
    "RepositoryRpcGetModelDownloadOptionsReturns",
    "RepositoryRpcGetModelDownloadOptionsReturnsDict",
    "RepositoryRpcInstallPluginDependenciesParameter",
    "RepositoryRpcInstallPluginDependenciesParameterDict",
    "RepositoryRpcLoginWithPreAuthenticatedKeysParameter",
    "RepositoryRpcLoginWithPreAuthenticatedKeysParameterDict",
    "RepositoryRpcLoginWithPreAuthenticatedKeysReturns",
    "RepositoryRpcLoginWithPreAuthenticatedKeysReturnsDict",
    "RepositoryRpcSearchModelsParameter",
    "RepositoryRpcSearchModelsParameterDict",
    "RepositoryRpcSearchModelsReturns",
    "RepositoryRpcSearchModelsReturnsDict",
    "RetrievalChunk",
    "RetrievalChunkDict",
    "RetrievalChunkingMethodRecursiveV1",
    "RetrievalChunkingMethodRecursiveV1Dict",
    "Runtime",
    "RuntimeDict",
    "SerializedKVConfigSchematics",
    "SerializedKVConfigSchematicsDict",
    "SerializedKVConfigSchematicsField",
    "SerializedKVConfigSchematicsFieldDict",
    "SerializedLMSExtendedError",
    "SerializedLMSExtendedErrorDict",
    "StatusStepState",
    "StatusStepStateDict",
    "SystemPrompt",
    "SystemPromptDict",
    "SystemRpcNotifyParameter",
    "SystemRpcNotifyParameterDict",
    "SystemRpcSetExperimentFlagParameter",
    "SystemRpcSetExperimentFlagParameterDict",
    "SystemRpcVersionReturns",
    "SystemRpcVersionReturnsDict",
    "TextData",
    "TextDataDict",
    "ToolCallRequest",
    "ToolCallRequestData",
    "ToolCallRequestDataDict",
    "ToolCallRequestDict",
    "ToolCallResultData",
    "ToolCallResultDataDict",
    "ToolResultMessage",
    "ToolResultMessageDict",
    "ToolStatusStepState",
    "ToolStatusStepStateDict",
    "ToolStatusStepStateStatusCallingTool",
    "ToolStatusStepStateStatusCallingToolDict",
    "ToolStatusStepStateStatusConfirmingToolCall",
    "ToolStatusStepStateStatusConfirmingToolCallDict",
    "ToolStatusStepStateStatusGeneratingToolCall",
    "ToolStatusStepStateStatusGeneratingToolCallDict",
    "ToolStatusStepStateStatusToolCallDenied",
    "ToolStatusStepStateStatusToolCallDeniedDict",
    "ToolStatusStepStateStatusToolCallFailed",
    "ToolStatusStepStateStatusToolCallFailedDict",
    "ToolStatusStepStateStatusToolCallGenerationFailed",
    "ToolStatusStepStateStatusToolCallGenerationFailedDict",
    "ToolStatusStepStateStatusToolCallQueued",
    "ToolStatusStepStateStatusToolCallQueuedDict",
    "ToolStatusStepStateStatusToolCallSucceeded",
    "ToolStatusStepStateStatusToolCallSucceededDict",
    "UserMessage",
    "UserMessageDict",
    "VirtualModelBooleanCustomFieldDefinition",
    "VirtualModelBooleanCustomFieldDefinitionDict",
    "VirtualModelConditionEquals",
    "VirtualModelConditionEqualsDict",
    "VirtualModelCustomFieldAppendSystemPromptEffect",
    "VirtualModelCustomFieldAppendSystemPromptEffectDict",
    "VirtualModelCustomFieldDefinitionBase",
    "VirtualModelCustomFieldDefinitionBaseDict",
    "VirtualModelCustomFieldPrependSystemPromptEffect",
    "VirtualModelCustomFieldPrependSystemPromptEffectDict",
    "VirtualModelCustomFieldSetJinjaVariableEffect",
    "VirtualModelCustomFieldSetJinjaVariableEffectDict",
    "VirtualModelDefinition",
    "VirtualModelDefinitionConcreteModelBase",
    "VirtualModelDefinitionConcreteModelBaseDict",
    "VirtualModelDefinitionDict",
    "VirtualModelDefinitionMetadataOverrides",
    "VirtualModelDefinitionMetadataOverridesDict",
    "VirtualModelStringCustomFieldDefinition",
    "VirtualModelStringCustomFieldDefinitionDict",
    "VirtualModelSuggestion",
    "VirtualModelSuggestionDict",
]


class BackendNotification(LMStudioStruct["BackendNotificationDict"], kw_only=True):
    title: str
    description: str | None = None
    no_auto_dismiss: bool | None = field(name="noAutoDismiss", default=None)


class BackendNotificationDict(TypedDict):
    """Corresponding typed dictionary definition for BackendNotification.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    title: str
    description: NotRequired[str | None]
    noAutoDismiss: NotRequired[bool | None]


class TextData(
    LMStudioStruct["TextDataDict"], kw_only=True, tag_field="type", tag="text"
):
    type: ClassVar[Annotated[Literal["text"], Meta(title="Type")]] = "text"
    text: str


class TextDataDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessagePartTextData.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["text"]
    text: str


class ToolCallResultData(
    LMStudioStruct["ToolCallResultDataDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallResult",
):
    type: ClassVar[Annotated[Literal["toolCallResult"], Meta(title="Type")]] = (
        "toolCallResult"
    )
    content: str
    tool_call_id: str | None = field(name="toolCallId", default=None)


class ToolCallResultDataDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessagePartToolCallResultData.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallResult"]
    content: str
    toolCallId: NotRequired[str | None]


ChatMessageRoleData = Literal["assistant", "user", "system", "tool"]
PageNumber = Sequence[int]
LineNumber = Sequence[int]


class CitationSource(LMStudioStruct["CitationSourceDict"], kw_only=True):
    file_name: str = field(name="fileName")
    absolute_file_path: str | None = field(name="absoluteFilePath", default=None)
    page_number: int | PageNumber | None = field(name="pageNumber", default=None)
    line_number: int | LineNumber | None = field(name="lineNumber", default=None)


class CitationSourceDict(TypedDict):
    """Corresponding typed dictionary definition for CitationSource.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fileName: str
    absoluteFilePath: NotRequired[str | None]
    pageNumber: NotRequired[int | PageNumber | None]
    lineNumber: NotRequired[int | LineNumber | None]


ColorPalette = Literal["red", "green", "blue", "yellow", "orange", "purple", "default"]


class EmbeddingModelAdditionalInfo(
    LMStudioStruct["EmbeddingModelAdditionalInfoDict"], kw_only=True
):
    max_context_length: int = field(name="maxContextLength")


class EmbeddingModelAdditionalInfoDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingModelAdditionalInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    maxContextLength: int


class EmbeddingModelInstanceAdditionalInfo(
    LMStudioStruct["EmbeddingModelInstanceAdditionalInfoDict"], kw_only=True
):
    context_length: int = field(name="contextLength")


class EmbeddingModelInstanceAdditionalInfoDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingModelInstanceAdditionalInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    contextLength: int


class SerializedLMSExtendedError(
    LMStudioStruct["SerializedLMSExtendedErrorDict"], kw_only=True
):
    title: Any | None = "Unknown error"
    cause: Any | None = None
    suggestion: Any | None = None
    error_data: Any | None = field(name="errorData", default=None)
    display_data: Any | None = field(name="displayData", default=None)
    stack: Any | None = None
    root_title: Any | None = field(name="rootTitle", default=None)


class SerializedLMSExtendedErrorDict(TypedDict):
    """Corresponding typed dictionary definition for SerializedLMSExtendedError.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    title: NotRequired[Any | None]
    cause: NotRequired[Any | None]
    suggestion: NotRequired[Any | None]
    errorData: NotRequired[Any | None]
    displayData: NotRequired[Any | None]
    stack: NotRequired[Any | None]
    rootTitle: NotRequired[Any | None]


class DocumentParsingLibraryIdentifier(
    LMStudioStruct["DocumentParsingLibraryIdentifierDict"], kw_only=True
):
    library: str
    version: str


class DocumentParsingLibraryIdentifierDict(TypedDict):
    """Corresponding typed dictionary definition for DocumentParsingLibraryIdentifier.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    library: str
    version: str


class DocumentParsingOpts(LMStudioStruct["DocumentParsingOptsDict"], kw_only=True):
    parser_id: DocumentParsingLibraryIdentifier | None = field(
        name="parserId", default=None
    )


class DocumentParsingOptsDict(TypedDict):
    """Corresponding typed dictionary definition for DocumentParsingOpts.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parserId: NotRequired[DocumentParsingLibraryIdentifierDict | None]


FileNamespace = Literal["local", "base64"]
FileType = Literal[
    "image",
    "text/plain",
    "application/pdf",
    "application/word",
    "text/other",
    "unknown",
]
DisabledGpu = Annotated[int, Meta(ge=0)]
PriorityItem = Annotated[int, Meta(ge=0)]
CustomRatioItem = Annotated[float, Meta(ge=0.0)]
GpuSplitStrategy = Literal["evenly", "priorityOrder", "custom"]
JsonSerializable = Any
KebabCase = Annotated[str, Meta(pattern="^[a-z0-9]+(?:-[a-z0-9]+)*$")]
KebabCaseWithDots = Annotated[str, Meta(pattern="^[a-z0-9]+(?:[-.][a-z0-9]+)*$")]


class KvConfigField(LMStudioStruct["KvConfigFieldDict"], kw_only=True):
    key: str
    value: Any | None = None


class KvConfigFieldDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfigField.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    key: str
    value: NotRequired[Any | None]


KvConfigLayerName = Literal[
    "currentlyEditing",
    "currentlyLoaded",
    "apiOverride",
    "conversationSpecific",
    "conversationGlobal",
    "preset",
    "serverSession",
    "httpServerRequestOverride",
    "completeModeFormatting",
    "instance",
    "userModelDefault",
    "virtualModel",
    "modelDefault",
    "hardware",
]


class KvConfig(LMStudioStruct["KvConfigDict"], kw_only=True):
    fields: Sequence[KvConfigField]


class KvConfigDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fields: Sequence[KvConfigFieldDict]


class KvConfigStackLayer(LMStudioStruct["KvConfigStackLayerDict"], kw_only=True):
    layer_name: KvConfigLayerName = field(name="layerName")
    config: KvConfig


class KvConfigStackLayerDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfigStackLayer.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    layerName: KvConfigLayerName
    config: KvConfigDict


class KvConfigStack(LMStudioStruct["KvConfigStackDict"], kw_only=True):
    layers: Sequence[KvConfigStackLayer]


class KvConfigStackDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfigStack.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    layers: Sequence[KvConfigStackLayerDict]


LlmLlamaAccelerationOffloadRatio1 = Annotated[float, Meta(ge=0.0, le=1.0)]
LlmLlamaAccelerationOffloadRatio = LlmLlamaAccelerationOffloadRatio1 | str
LlmLlamaAccelerationOffloadRatioDict = float | str
LlmLlamaCacheQuantizationType = Literal[
    "f32", "f16", "q8_0", "q4_0", "q4_1", "iq4_nl", "q5_0", "q5_1"
]
LlmMlxKvCacheBitsType = Literal[8, 6, 4, 3, 2]
LlmMlxKvCacheGroupSizeTypes = Literal[32, 64, 128]


class LlmMlxKvCacheQuantization(
    LMStudioStruct["LlmMlxKvCacheQuantizationDict"], kw_only=True
):
    enabled: bool
    bits: LlmMlxKvCacheBitsType
    group_size: LlmMlxKvCacheGroupSizeTypes = field(name="groupSize")
    quantized_start: Annotated[int, Meta(ge=0)] = field(name="quantizedStart")


class LlmMlxKvCacheQuantizationDict(TypedDict):
    """Corresponding typed dictionary definition for LlmMlxKvCacheQuantization.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    enabled: bool
    bits: LlmMlxKvCacheBitsType
    groupSize: LlmMlxKvCacheGroupSizeTypes
    quantizedStart: Annotated[int, Meta(ge=0)]


LlmSplitStrategy = Literal["evenly", "favorMainGpu"]


class LlmAdditionalInfo(LMStudioStruct["LlmAdditionalInfoDict"], kw_only=True):
    vision: bool
    trained_for_tool_use: bool = field(name="trainedForToolUse")
    max_context_length: int = field(name="maxContextLength")


class LlmAdditionalInfoDict(TypedDict):
    """Corresponding typed dictionary definition for LlmAdditionalInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    vision: bool
    trainedForToolUse: bool
    maxContextLength: int


class LlmInstanceAdditionalInfo(
    LMStudioStruct["LlmInstanceAdditionalInfoDict"], kw_only=True
):
    context_length: int = field(name="contextLength")


class LlmInstanceAdditionalInfoDict(TypedDict):
    """Corresponding typed dictionary definition for LlmInstanceAdditionalInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    contextLength: int


LlmContextOverflowPolicy = Literal["stopAtLimit", "truncateMiddle", "rollingWindow"]


class LlmLlamaMirostatSamplingConfig(
    LMStudioStruct["LlmLlamaMirostatSamplingConfigDict"], kw_only=True
):
    version: Literal[0, 1, 2]
    learning_rate: float = field(name="learningRate")
    target_entropy: float = field(name="targetEntropy")


class LlmLlamaMirostatSamplingConfigDict(TypedDict):
    """Corresponding typed dictionary definition for LlmLlamaMirostatSamplingConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    version: Literal[0, 1, 2]
    learningRate: float
    targetEntropy: float


LlmLlamaSingleLogitBiasModification = float | str
MaxTokens = Annotated[int, Meta(ge=-1)]


class LlmReasoningParsing(LMStudioStruct["LlmReasoningParsingDict"], kw_only=True):
    enabled: bool
    start_string: str = field(name="startString")
    end_string: str = field(name="endString")


class LlmReasoningParsingDict(TypedDict):
    """Corresponding typed dictionary definition for LlmReasoningParsing.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    enabled: bool
    startString: str
    endString: str


LlmPredictionFragmentReasoningType = Literal[
    "none", "reasoning", "reasoningStartTag", "reasoningEndTag"
]


class LlmPredictionFragment(LMStudioStruct["LlmPredictionFragmentDict"], kw_only=True):
    content: str
    tokens_count: int = field(name="tokensCount")
    contains_drafted: bool = field(name="containsDrafted")
    reasoning_type: LlmPredictionFragmentReasoningType = field(name="reasoningType")


class LlmPredictionFragmentDict(TypedDict):
    """Corresponding typed dictionary definition for LlmPredictionFragment.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    content: str
    tokensCount: int
    containsDrafted: bool
    reasoningType: LlmPredictionFragmentReasoningType


LlmPredictionStopReason = Literal[
    "userStopped",
    "modelUnloaded",
    "failed",
    "eosFound",
    "stopStringFound",
    "toolCalls",
    "maxPredictedTokensReached",
    "contextLengthReached",
]


class LlmJinjaPromptTemplate(
    LMStudioStruct["LlmJinjaPromptTemplateDict"], kw_only=True
):
    template: str


class LlmJinjaPromptTemplateDict(TypedDict):
    """Corresponding typed dictionary definition for LlmJinjaPromptTemplate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    template: str


class LlmManualPromptTemplate(
    LMStudioStruct["LlmManualPromptTemplateDict"], kw_only=True
):
    before_system: str = field(name="beforeSystem")
    after_system: str = field(name="afterSystem")
    before_user: str = field(name="beforeUser")
    after_user: str = field(name="afterUser")
    before_assistant: str = field(name="beforeAssistant")
    after_assistant: str = field(name="afterAssistant")


class LlmManualPromptTemplateDict(TypedDict):
    """Corresponding typed dictionary definition for LlmManualPromptTemplate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    beforeSystem: str
    afterSystem: str
    beforeUser: str
    afterUser: str
    beforeAssistant: str
    afterAssistant: str


LlmPromptTemplateType = Literal["manual", "jinja"]
LlmStructuredPredictionType = Literal["none", "json", "gbnf"]


class ProcessingRequestConfirmToolCall(
    LMStudioStruct["ProcessingRequestConfirmToolCallDict"],
    kw_only=True,
    tag_field="type",
    tag="confirmToolCall",
):
    type: ClassVar[Annotated[Literal["confirmToolCall"], Meta(title="Type")]] = (
        "confirmToolCall"
    )
    call_id: int = field(name="callId")
    name: str
    parameters: Mapping[str, Any]
    plugin_identifier: str | None = field(name="pluginIdentifier", default=None)


class ProcessingRequestConfirmToolCallDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingRequestConfirmToolCall.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["confirmToolCall"]
    callId: int
    name: str
    parameters: Mapping[str, Any]
    pluginIdentifier: NotRequired[str | None]


class ProcessingRequestResponseTextInput(
    LMStudioStruct["ProcessingRequestResponseTextInputDict"],
    kw_only=True,
    tag_field="type",
    tag="textInput",
):
    type: ClassVar[Annotated[Literal["textInput"], Meta(title="Type")]] = "textInput"
    result: str


class ProcessingRequestResponseTextInputDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingRequestResponseTextInput.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["textInput"]
    result: str


class ProcessingRequestTextInput(
    LMStudioStruct["ProcessingRequestTextInputDict"],
    kw_only=True,
    tag_field="type",
    tag="textInput",
):
    type: ClassVar[Annotated[Literal["textInput"], Meta(title="Type")]] = "textInput"
    prompt: str


class ProcessingRequestTextInputDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingRequestTextInput.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["textInput"]
    prompt: str


class ProcessingUpdateCitationBlockCreate(
    LMStudioStruct["ProcessingUpdateCitationBlockCreateDict"],
    kw_only=True,
    tag_field="type",
    tag="citationBlock.create",
):
    type: ClassVar[Annotated[Literal["citationBlock.create"], Meta(title="Type")]] = (
        "citationBlock.create"
    )
    id: str
    cited_text: str = field(name="citedText")
    file_name: str = field(name="fileName")
    file_identifier: str = field(name="fileIdentifier")
    page_number: int | PageNumber | None = field(name="pageNumber", default=None)
    line_number: int | LineNumber | None = field(name="lineNumber", default=None)


class ProcessingUpdateCitationBlockCreateDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateCitationBlockCreate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["citationBlock.create"]
    id: str
    citedText: str
    fileName: str
    fileIdentifier: str
    pageNumber: NotRequired[int | PageNumber | None]
    lineNumber: NotRequired[int | LineNumber | None]


class ProcessingUpdateContentBlockAppendText(
    LMStudioStruct["ProcessingUpdateContentBlockAppendTextDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.appendText",
):
    type: ClassVar[
        Annotated[Literal["contentBlock.appendText"], Meta(title="Type")]
    ] = "contentBlock.appendText"
    id: str
    text: str
    tokens_count: int | None = field(name="tokensCount", default=None)
    from_draft_model: bool | None = field(name="fromDraftModel", default=None)


class ProcessingUpdateContentBlockAppendTextDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockAppendText.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.appendText"]
    id: str
    text: str
    tokensCount: NotRequired[int | None]
    fromDraftModel: NotRequired[bool | None]


class ProcessingUpdateContentBlockAppendToolRequest(
    LMStudioStruct["ProcessingUpdateContentBlockAppendToolRequestDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.appendToolRequest",
):
    type: ClassVar[
        Annotated[Literal["contentBlock.appendToolRequest"], Meta(title="Type")]
    ] = "contentBlock.appendToolRequest"
    id: str
    call_id: int = field(name="callId")
    name: str
    parameters: Mapping[str, Any]
    tool_call_request_id: str | None = field(name="toolCallRequestId", default=None)
    plugin_identifier: str | None = field(name="pluginIdentifier", default=None)


class ProcessingUpdateContentBlockAppendToolRequestDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockAppendToolRequest.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.appendToolRequest"]
    id: str
    callId: int
    name: str
    parameters: Mapping[str, Any]
    toolCallRequestId: NotRequired[str | None]
    pluginIdentifier: NotRequired[str | None]


class ProcessingUpdateContentBlockAppendToolResult(
    LMStudioStruct["ProcessingUpdateContentBlockAppendToolResultDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.appendToolResult",
):
    type: ClassVar[
        Annotated[Literal["contentBlock.appendToolResult"], Meta(title="Type")]
    ] = "contentBlock.appendToolResult"
    id: str
    call_id: int = field(name="callId")
    content: str
    tool_call_request_id: str | None = field(name="toolCallRequestId", default=None)


class ProcessingUpdateContentBlockAppendToolResultDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockAppendToolResult.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.appendToolResult"]
    id: str
    callId: int
    content: str
    toolCallRequestId: NotRequired[str | None]


class ProcessingUpdateContentBlockReplaceText(
    LMStudioStruct["ProcessingUpdateContentBlockReplaceTextDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.replaceText",
):
    type: ClassVar[
        Annotated[Literal["contentBlock.replaceText"], Meta(title="Type")]
    ] = "contentBlock.replaceText"
    id: str
    text: str


class ProcessingUpdateContentBlockReplaceTextDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockReplaceText.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.replaceText"]
    id: str
    text: str


class ProcessingUpdateContentBlockReplaceToolRequest(
    LMStudioStruct["ProcessingUpdateContentBlockReplaceToolRequestDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.replaceToolRequest",
):
    type: ClassVar[
        Annotated[Literal["contentBlock.replaceToolRequest"], Meta(title="Type")]
    ] = "contentBlock.replaceToolRequest"
    id: str
    call_id: int = field(name="callId")
    name: str
    parameters: Mapping[str, Any]
    tool_call_request_id: str | None = field(name="toolCallRequestId", default=None)
    plugin_identifier: str | None = field(name="pluginIdentifier", default=None)


class ProcessingUpdateContentBlockReplaceToolRequestDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockReplaceToolRequest.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.replaceToolRequest"]
    id: str
    callId: int
    name: str
    parameters: Mapping[str, Any]
    toolCallRequestId: NotRequired[str | None]
    pluginIdentifier: NotRequired[str | None]


class ProcessingUpdateContentBlockSetPrefix(
    LMStudioStruct["ProcessingUpdateContentBlockSetPrefixDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.setPrefix",
):
    type: ClassVar[Annotated[Literal["contentBlock.setPrefix"], Meta(title="Type")]] = (
        "contentBlock.setPrefix"
    )
    id: str
    prefix: str


class ProcessingUpdateContentBlockSetPrefixDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockSetPrefix.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.setPrefix"]
    id: str
    prefix: str


class ProcessingUpdateContentBlockSetSuffix(
    LMStudioStruct["ProcessingUpdateContentBlockSetSuffixDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.setSuffix",
):
    type: ClassVar[Annotated[Literal["contentBlock.setSuffix"], Meta(title="Type")]] = (
        "contentBlock.setSuffix"
    )
    id: str
    suffix: str


class ProcessingUpdateContentBlockSetSuffixDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockSetSuffix.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.setSuffix"]
    id: str
    suffix: str


class ProcessingUpdateDebugInfoBlockCreate(
    LMStudioStruct["ProcessingUpdateDebugInfoBlockCreateDict"],
    kw_only=True,
    tag_field="type",
    tag="debugInfoBlock.create",
):
    type: ClassVar[Annotated[Literal["debugInfoBlock.create"], Meta(title="Type")]] = (
        "debugInfoBlock.create"
    )
    id: str
    debug_info: str = field(name="debugInfo")


class ProcessingUpdateDebugInfoBlockCreateDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateDebugInfoBlockCreate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["debugInfoBlock.create"]
    id: str
    debugInfo: str


class ProcessingUpdateSetSenderName(
    LMStudioStruct["ProcessingUpdateSetSenderNameDict"],
    kw_only=True,
    tag_field="type",
    tag="setSenderName",
):
    type: ClassVar[Annotated[Literal["setSenderName"], Meta(title="Type")]] = (
        "setSenderName"
    )
    name: str


class ProcessingUpdateSetSenderNameDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateSetSenderName.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["setSenderName"]
    name: str


class ProcessingUpdateStatusRemove(
    LMStudioStruct["ProcessingUpdateStatusRemoveDict"],
    kw_only=True,
    tag_field="type",
    tag="status.remove",
):
    type: ClassVar[Annotated[Literal["status.remove"], Meta(title="Type")]] = (
        "status.remove"
    )
    id: str


class ProcessingUpdateStatusRemoveDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateStatusRemove.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["status.remove"]
    id: str


class ProcessingUpdateToolStatusArgumentFragment(
    LMStudioStruct["ProcessingUpdateToolStatusArgumentFragmentDict"],
    kw_only=True,
    tag_field="type",
    tag="toolStatus.argumentFragment",
):
    type: ClassVar[
        Annotated[Literal["toolStatus.argumentFragment"], Meta(title="Type")]
    ] = "toolStatus.argumentFragment"
    id: str
    content: str


class ProcessingUpdateToolStatusArgumentFragmentDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateToolStatusArgumentFragment.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolStatus.argumentFragment"]
    id: str
    content: str


StatusStepStatus = Literal["waiting", "loading", "done", "error", "canceled"]


class GetModelOpts(LMStudioStruct["GetModelOptsDict"], kw_only=True):
    model_tag: str | None = field(name="modelTag", default=None)
    ignore_user_config: bool | None = field(name="ignoreUserConfig", default=None)


class GetModelOptsDict(TypedDict):
    """Corresponding typed dictionary definition for GetModelOpts.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelTag: NotRequired[str | None]
    ignoreUserConfig: NotRequired[bool | None]


ModelCompatibilityType = Literal[
    "gguf", "safetensors", "onnx", "ggml", "mlx_placeholder", "torch_safetensors"
]
ModelDomainType = Literal["llm", "embedding", "imageGen", "transcription", "tts"]
FileName = Annotated[
    str,
    Meta(
        pattern="^[..!@#$%^&()\\-_+=,.;'[\\]{}~`][..!@#$%^&()\\-_+=,.;'[\\]{}~` ]*(?<![. ])$"
    ),
]
RelativePathNoLeadingDotSlash = Annotated[
    str,
    Meta(
        pattern="^[..!@#$%^&()\\-_+=,.;'[\\]{}~`][..!@#$%^&()\\-_+=,.;'[\\]{}~` ]*(?<![. ])(?:\\/[..!@#$%^&()\\-_+=,.;'[\\]{}~`][..!@#$%^&()\\-_+=,.;'[\\]{}~` ]*(?<![. ]))*$"
    ),
]
PluginRunnerType = Literal["ecmascript", "node", "mcpBridge"]
ReasonableKeyString = Annotated[str, Meta(max_length=1024, min_length=1)]


class ArtifactDownloadPlanModelInfo(
    LMStudioStruct["ArtifactDownloadPlanModelInfoDict"], kw_only=True
):
    display_name: str = field(name="displayName")
    size_bytes: float = field(name="sizeBytes")
    compatibility_type: ModelCompatibilityType = field(name="compatibilityType")
    quant_name: str | None = field(name="quantName", default=None)


class ArtifactDownloadPlanModelInfoDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactDownloadPlanModelInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    displayName: str
    sizeBytes: float
    compatibilityType: ModelCompatibilityType
    quantName: NotRequired[str | None]


ArtifactDownloadPlanNodeState = Literal["pending", "fetching", "satisfied", "completed"]


class LocalArtifactFileEntry(
    LMStudioStruct["LocalArtifactFileEntryDict"], kw_only=True
):
    relative_path: str = field(name="relativePath")
    size_bytes: int = field(name="sizeBytes")


class LocalArtifactFileEntryDict(TypedDict):
    """Corresponding typed dictionary definition for LocalArtifactFileEntry.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    relativePath: str
    sizeBytes: int


class LocalArtifactFileList(LMStudioStruct["LocalArtifactFileListDict"], kw_only=True):
    files: Sequence[LocalArtifactFileEntry]
    used_ignore_file: str | None = field(name="usedIgnoreFile")


class LocalArtifactFileListDict(TypedDict):
    """Corresponding typed dictionary definition for LocalArtifactFileList.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    files: Sequence[LocalArtifactFileEntryDict]
    usedIgnoreFile: NotRequired[str | None]


class DownloadProgressUpdate(
    LMStudioStruct["DownloadProgressUpdateDict"], kw_only=True
):
    downloaded_bytes: int = field(name="downloadedBytes")
    total_bytes: int = field(name="totalBytes")
    speed_bytes_per_second: float = field(name="speedBytesPerSecond")


class DownloadProgressUpdateDict(TypedDict):
    """Corresponding typed dictionary definition for DownloadProgressUpdate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    downloadedBytes: int
    totalBytes: int
    speedBytesPerSecond: float


class ModelSearchOpts(LMStudioStruct["ModelSearchOptsDict"], kw_only=True):
    search_term: str | None = field(name="searchTerm", default=None)
    limit: Annotated[int, Meta(gt=0, le=25)] | None = None
    compatibility_types: Sequence[ModelCompatibilityType] | None = field(
        name="compatibilityTypes", default=None
    )


class ModelSearchOptsDict(TypedDict):
    """Corresponding typed dictionary definition for ModelSearchOpts.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    searchTerm: NotRequired[str | None]
    limit: NotRequired[Annotated[int, Meta(gt=0, le=25)] | None]
    compatibilityTypes: NotRequired[Sequence[ModelCompatibilityType] | None]


class ModelSearchResultDownloadOptionData(
    LMStudioStruct["ModelSearchResultDownloadOptionDataDict"], kw_only=True
):
    name: str
    size_bytes: int = field(name="sizeBytes")
    fit_estimation: Literal[
        "fullGPUOffload", "partialGPUOffload", "fitWithoutGPU", "willNotFit"
    ] = field(name="fitEstimation")
    download_identifier: str = field(name="downloadIdentifier")
    indexed_model_identifier: str = field(name="indexedModelIdentifier")
    quantization: str | None = None
    recommended: bool | None = None


class ModelSearchResultDownloadOptionDataDict(TypedDict):
    """Corresponding typed dictionary definition for ModelSearchResultDownloadOptionData.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    name: str
    sizeBytes: int
    fitEstimation: Literal[
        "fullGPUOffload", "partialGPUOffload", "fitWithoutGPU", "willNotFit"
    ]
    downloadIdentifier: str
    indexedModelIdentifier: str
    quantization: NotRequired[str | None]
    recommended: NotRequired[bool | None]


class InternalRetrievalResultEntry(
    LMStudioStruct["InternalRetrievalResultEntryDict"], kw_only=True
):
    content: str
    score: float
    source_index: int = field(name="sourceIndex")
    page_number: int | PageNumber | None = field(name="pageNumber", default=None)
    line_number: int | LineNumber | None = field(name="lineNumber", default=None)


class InternalRetrievalResultEntryDict(TypedDict):
    """Corresponding typed dictionary definition for InternalRetrievalResultEntry.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    content: str
    score: float
    sourceIndex: int
    pageNumber: NotRequired[int | PageNumber | None]
    lineNumber: NotRequired[int | LineNumber | None]


class InternalRetrievalResult(
    LMStudioStruct["InternalRetrievalResultDict"], kw_only=True
):
    entries: Sequence[InternalRetrievalResultEntry]


class InternalRetrievalResultDict(TypedDict):
    """Corresponding typed dictionary definition for InternalRetrievalResult.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    entries: Sequence[InternalRetrievalResultEntryDict]


class RetrievalChunk(LMStudioStruct["RetrievalChunkDict"], kw_only=True):
    content: str
    score: float
    citation: CitationSource


class RetrievalChunkDict(TypedDict):
    """Corresponding typed dictionary definition for RetrievalChunk.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    content: str
    score: float
    citation: CitationSourceDict


RetrievalFileProcessingStep = Literal["loading", "chunking", "embedding"]
AcceleratorType = Literal["unknown", "integratedGpu", "dedicatedGpu"]


class KvConfigSchematicsDeserializationError(
    LMStudioStruct["KvConfigSchematicsDeserializationErrorDict"], kw_only=True
):
    full_key: str = field(name="fullKey")
    error: JsonSerializable


class KvConfigSchematicsDeserializationErrorDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfigSchematicsDeserializationError.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fullKey: str
    error: JsonSerializable


class SerializedKVConfigSchematicsField(
    LMStudioStruct["SerializedKVConfigSchematicsFieldDict"], kw_only=True
):
    short_key: str = field(name="shortKey")
    full_key: str = field(name="fullKey")
    type_key: str = field(name="typeKey")
    type_params: JsonSerializable = field(name="typeParams")
    default_value: JsonSerializable = field(name="defaultValue")


class SerializedKVConfigSchematicsFieldDict(TypedDict):
    """Corresponding typed dictionary definition for SerializedKVConfigSchematicsField.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    shortKey: str
    fullKey: str
    typeKey: str
    typeParams: JsonSerializable
    defaultValue: JsonSerializable


class SerializedKVConfigSchematics(
    LMStudioStruct["SerializedKVConfigSchematicsDict"], kw_only=True
):
    fields: Sequence[SerializedKVConfigSchematicsField]
    extension_prefixes: Sequence[str] | None = field(
        name="extensionPrefixes", default=None
    )


class SerializedKVConfigSchematicsDict(TypedDict):
    """Corresponding typed dictionary definition for SerializedKVConfigSchematics.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fields: Sequence[SerializedKVConfigSchematicsFieldDict]
    extensionPrefixes: NotRequired[Sequence[str] | None]


BooleanOrMixed = Literal[True, False, "mixed"]


class VirtualModelConditionEquals(
    LMStudioStruct["VirtualModelConditionEqualsDict"], kw_only=True
):
    type: Annotated[Literal["equals"], Meta(title="Type")]
    key: str
    value: JsonSerializable


class VirtualModelConditionEqualsDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelConditionEquals.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["equals"], Meta(title="Type")]
    key: str
    value: JsonSerializable


VirtualModelCondition = VirtualModelConditionEquals


class VirtualModelCustomFieldAppendSystemPromptEffect(
    LMStudioStruct["VirtualModelCustomFieldAppendSystemPromptEffectDict"],
    kw_only=True,
    tag_field="type",
    tag="appendSystemPrompt",
):
    type: ClassVar[Annotated[Literal["appendSystemPrompt"], Meta(title="Type")]] = (
        "appendSystemPrompt"
    )
    content: str


class VirtualModelCustomFieldAppendSystemPromptEffectDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelCustomFieldAppendSystemPromptEffect.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["appendSystemPrompt"]
    content: str


class VirtualModelCustomFieldPrependSystemPromptEffect(
    LMStudioStruct["VirtualModelCustomFieldPrependSystemPromptEffectDict"],
    kw_only=True,
    tag_field="type",
    tag="prependSystemPrompt",
):
    type: ClassVar[Annotated[Literal["prependSystemPrompt"], Meta(title="Type")]] = (
        "prependSystemPrompt"
    )
    content: str


class VirtualModelCustomFieldPrependSystemPromptEffectDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelCustomFieldPrependSystemPromptEffect.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["prependSystemPrompt"]
    content: str


class VirtualModelCustomFieldSetJinjaVariableEffect(
    LMStudioStruct["VirtualModelCustomFieldSetJinjaVariableEffectDict"],
    kw_only=True,
    tag_field="type",
    tag="setJinjaVariable",
):
    type: ClassVar[Annotated[Literal["setJinjaVariable"], Meta(title="Type")]] = (
        "setJinjaVariable"
    )
    variable: str


class VirtualModelCustomFieldSetJinjaVariableEffectDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelCustomFieldSetJinjaVariableEffect.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["setJinjaVariable"]
    variable: str


class VirtualModelDefinitionMetadataOverrides(
    LMStudioStruct["VirtualModelDefinitionMetadataOverridesDict"], kw_only=True
):
    domain: ModelDomainType | None = None
    architectures: Sequence[str] | None = None
    compatibility_types: Sequence[ModelCompatibilityType] | None = field(
        name="compatibilityTypes", default=None
    )
    params_strings: Sequence[str] | None = field(name="paramsStrings", default=None)
    min_memory_usage_bytes: float | None = field(
        name="minMemoryUsageBytes", default=None
    )
    context_lengths: Sequence[float] | None = field(name="contextLengths", default=None)
    trained_for_tool_use: BooleanOrMixed | None = field(
        name="trainedForToolUse", default=None
    )
    vision: BooleanOrMixed | None = None
    reasoning: BooleanOrMixed | None = None
    fim: BooleanOrMixed | None = None


class VirtualModelDefinitionMetadataOverridesDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelDefinitionMetadataOverrides.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    domain: NotRequired[ModelDomainType | None]
    architectures: NotRequired[Sequence[str] | None]
    compatibilityTypes: NotRequired[Sequence[ModelCompatibilityType] | None]
    paramsStrings: NotRequired[Sequence[str] | None]
    minMemoryUsageBytes: NotRequired[float | None]
    contextLengths: NotRequired[Sequence[float] | None]
    trainedForToolUse: NotRequired[BooleanOrMixed | None]
    vision: NotRequired[BooleanOrMixed | None]
    reasoning: NotRequired[BooleanOrMixed | None]
    fim: NotRequired[BooleanOrMixed | None]


Tag = Annotated[str, Meta(max_length=100)]


class Config(LMStudioStruct["ConfigDict"], kw_only=True):
    load: KvConfig | None = None
    operation: KvConfig | None = None


class ConfigDict(TypedDict):
    """Corresponding typed dictionary definition for Config.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    load: NotRequired[KvConfigDict | None]
    operation: NotRequired[KvConfigDict | None]


class VirtualModelSuggestion(
    LMStudioStruct["VirtualModelSuggestionDict"], kw_only=True
):
    message: str
    conditions: Sequence[VirtualModelCondition]
    fields: Sequence[KvConfigField] | None = None


class VirtualModelSuggestionDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelSuggestion.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    message: str
    conditions: Sequence[VirtualModelConditionEqualsDict]
    fields: NotRequired[Sequence[KvConfigFieldDict] | None]


ZodSchema = Any


class EmbeddingRpcUnloadModelParameter(
    LMStudioStruct["EmbeddingRpcUnloadModelParameterDict"], kw_only=True
):
    identifier: str


class EmbeddingRpcUnloadModelParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcUnloadModelParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    identifier: str


EmbeddingRpcUnloadModelReturns = Any


class PseudoEmbeddingRpcUnloadModel(
    LMStudioStruct["PseudoEmbeddingRpcUnloadModelDict"], kw_only=True
):
    parameter: EmbeddingRpcUnloadModelParameter


class PseudoEmbeddingRpcUnloadModelDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingRpcUnloadModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: EmbeddingRpcUnloadModelParameterDict


EmbeddingRpcListLoadedParameter = Any


class EmbeddingRpcEmbedStringReturns(
    LMStudioStruct["EmbeddingRpcEmbedStringReturnsDict"], kw_only=True
):
    embedding: Sequence[float]


class EmbeddingRpcEmbedStringReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcEmbedStringReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    embedding: Sequence[float]


class EmbeddingRpcTokenizeReturns(
    LMStudioStruct["EmbeddingRpcTokenizeReturnsDict"], kw_only=True
):
    tokens: Sequence[float]


class EmbeddingRpcTokenizeReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcTokenizeReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    tokens: Sequence[float]


class EmbeddingRpcCountTokensReturns(
    LMStudioStruct["EmbeddingRpcCountTokensReturnsDict"], kw_only=True
):
    token_count: int = field(name="tokenCount")


class EmbeddingRpcCountTokensReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcCountTokensReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    tokenCount: int


class EmbeddingChannelLoadModelCreationParameter(
    LMStudioStruct["EmbeddingChannelLoadModelCreationParameterDict"], kw_only=True
):
    model_key: str = field(name="modelKey")
    load_config_stack: KvConfigStack = field(name="loadConfigStack")
    identifier: str | None = None
    ttl_ms: Annotated[int, Meta(ge=1)] | None = field(name="ttlMs", default=None)


class EmbeddingChannelLoadModelCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelLoadModelCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelKey: str
    loadConfigStack: KvConfigStackDict
    identifier: NotRequired[str | None]
    ttlMs: NotRequired[Annotated[int, Meta(ge=1)] | None]


class EmbeddingChannelGetOrLoadCreationParameter(
    LMStudioStruct["EmbeddingChannelGetOrLoadCreationParameterDict"], kw_only=True
):
    identifier: str
    load_config_stack: KvConfigStack = field(name="loadConfigStack")
    load_ttl_ms: Annotated[int, Meta(ge=1)] | None = field(
        name="loadTtlMs", default=None
    )


class EmbeddingChannelGetOrLoadCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelGetOrLoadCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    identifier: str
    loadConfigStack: KvConfigStackDict
    loadTtlMs: NotRequired[Annotated[int, Meta(ge=1)] | None]


class FilesRpcGetLocalFileAbsolutePathParameter(
    LMStudioStruct["FilesRpcGetLocalFileAbsolutePathParameterDict"], kw_only=True
):
    file_name: str = field(name="fileName")


class FilesRpcGetLocalFileAbsolutePathParameterDict(TypedDict):
    """Corresponding typed dictionary definition for FilesRpcGetLocalFileAbsolutePathParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fileName: str


class FilesRpcGetLocalFileAbsolutePathReturns(
    LMStudioStruct["FilesRpcGetLocalFileAbsolutePathReturnsDict"], kw_only=True
):
    path: str


class FilesRpcGetLocalFileAbsolutePathReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for FilesRpcGetLocalFileAbsolutePathReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    path: str


class PseudoFilesRpcGetLocalFileAbsolutePath(
    LMStudioStruct["PseudoFilesRpcGetLocalFileAbsolutePathDict"], kw_only=True
):
    parameter: FilesRpcGetLocalFileAbsolutePathParameter
    returns: FilesRpcGetLocalFileAbsolutePathReturns


class PseudoFilesRpcGetLocalFileAbsolutePathDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoFilesRpcGetLocalFileAbsolutePath.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: FilesRpcGetLocalFileAbsolutePathParameterDict
    returns: FilesRpcGetLocalFileAbsolutePathReturnsDict


class FilesRpcUploadFileBase64Parameter(
    LMStudioStruct["FilesRpcUploadFileBase64ParameterDict"], kw_only=True
):
    name: str
    content_base64: str = field(name="contentBase64")


class FilesRpcUploadFileBase64ParameterDict(TypedDict):
    """Corresponding typed dictionary definition for FilesRpcUploadFileBase64Parameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    name: str
    contentBase64: str


class FilesRpcUploadFileBase64Returns(
    LMStudioStruct["FilesRpcUploadFileBase64ReturnsDict"], kw_only=True
):
    identifier: str
    file_type: FileType = field(name="fileType")
    size_bytes: int = field(name="sizeBytes")


class FilesRpcUploadFileBase64ReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for FilesRpcUploadFileBase64Returns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    identifier: str
    fileType: FileType
    sizeBytes: int


class PseudoFilesRpcUploadFileBase64(
    LMStudioStruct["PseudoFilesRpcUploadFileBase64Dict"], kw_only=True
):
    parameter: FilesRpcUploadFileBase64Parameter
    returns: FilesRpcUploadFileBase64Returns


class PseudoFilesRpcUploadFileBase64Dict(TypedDict):
    """Corresponding typed dictionary definition for PseudoFilesRpcUploadFileBase64.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: FilesRpcUploadFileBase64ParameterDict
    returns: FilesRpcUploadFileBase64ReturnsDict


class FilesRpcGetDocumentParsingLibraryParameter(
    LMStudioStruct["FilesRpcGetDocumentParsingLibraryParameterDict"], kw_only=True
):
    file_identifier: str = field(name="fileIdentifier")


class FilesRpcGetDocumentParsingLibraryParameterDict(TypedDict):
    """Corresponding typed dictionary definition for FilesRpcGetDocumentParsingLibraryParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fileIdentifier: str


class FilesRpcGetDocumentParsingLibraryReturns(
    LMStudioStruct["FilesRpcGetDocumentParsingLibraryReturnsDict"], kw_only=True
):
    library: str
    version: str


class FilesRpcGetDocumentParsingLibraryReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for FilesRpcGetDocumentParsingLibraryReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    library: str
    version: str


class PseudoFilesRpcGetDocumentParsingLibrary(
    LMStudioStruct["PseudoFilesRpcGetDocumentParsingLibraryDict"], kw_only=True
):
    parameter: FilesRpcGetDocumentParsingLibraryParameter
    returns: FilesRpcGetDocumentParsingLibraryReturns


class PseudoFilesRpcGetDocumentParsingLibraryDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoFilesRpcGetDocumentParsingLibrary.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: FilesRpcGetDocumentParsingLibraryParameterDict
    returns: FilesRpcGetDocumentParsingLibraryReturnsDict


class FilesChannelParseDocumentCreationParameter(
    LMStudioStruct["FilesChannelParseDocumentCreationParameterDict"], kw_only=True
):
    file_identifier: str = field(name="fileIdentifier")
    parse_opts: DocumentParsingOpts = field(name="parseOpts")


class FilesChannelParseDocumentCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelParseDocumentCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fileIdentifier: str
    parseOpts: DocumentParsingOptsDict


class LlmRpcUnloadModelParameter(
    LMStudioStruct["LlmRpcUnloadModelParameterDict"], kw_only=True
):
    identifier: str


class LlmRpcUnloadModelParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcUnloadModelParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    identifier: str


LlmRpcUnloadModelReturns = Any


class PseudoLlmRpcUnloadModel(
    LMStudioStruct["PseudoLlmRpcUnloadModelDict"], kw_only=True
):
    parameter: LlmRpcUnloadModelParameter


class PseudoLlmRpcUnloadModelDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcUnloadModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: LlmRpcUnloadModelParameterDict


LlmRpcListLoadedParameter = Any


class LlmRpcApplyPromptTemplateReturns(
    LMStudioStruct["LlmRpcApplyPromptTemplateReturnsDict"], kw_only=True
):
    formatted: str


class LlmRpcApplyPromptTemplateReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcApplyPromptTemplateReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    formatted: str


class LlmRpcTokenizeReturns(LMStudioStruct["LlmRpcTokenizeReturnsDict"], kw_only=True):
    tokens: Sequence[float]


class LlmRpcTokenizeReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcTokenizeReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    tokens: Sequence[float]


class LlmRpcCountTokensReturns(
    LMStudioStruct["LlmRpcCountTokensReturnsDict"], kw_only=True
):
    token_count: int = field(name="tokenCount")


class LlmRpcCountTokensReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcCountTokensReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    tokenCount: int


LlmRpcPreloadDraftModelReturns = Any


class LlmChannelLoadModelCreationParameter(
    LMStudioStruct["LlmChannelLoadModelCreationParameterDict"], kw_only=True
):
    model_key: str = field(name="modelKey")
    load_config_stack: KvConfigStack = field(name="loadConfigStack")
    identifier: str | None = None
    ttl_ms: Annotated[int, Meta(ge=1)] | None = field(name="ttlMs", default=None)


class LlmChannelLoadModelCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelLoadModelCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelKey: str
    loadConfigStack: KvConfigStackDict
    identifier: NotRequired[str | None]
    ttlMs: NotRequired[Annotated[int, Meta(ge=1)] | None]


class LlmChannelGetOrLoadCreationParameter(
    LMStudioStruct["LlmChannelGetOrLoadCreationParameterDict"], kw_only=True
):
    identifier: str
    load_config_stack: KvConfigStack = field(name="loadConfigStack")
    load_ttl_ms: Annotated[int, Meta(ge=1)] | None = field(
        name="loadTtlMs", default=None
    )


class LlmChannelGetOrLoadCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGetOrLoadCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    identifier: str
    loadConfigStack: KvConfigStackDict
    loadTtlMs: NotRequired[Annotated[int, Meta(ge=1)] | None]


PluginsRpcReindexPluginsReturns = Any


class PseudoPluginsRpcReindexPlugins:
    pass


PluginsRpcProcessingHandleUpdateReturns = Any


class PluginsRpcProcessingPullHistoryParameter(
    LMStudioStruct["PluginsRpcProcessingPullHistoryParameterDict"], kw_only=True
):
    pci: str
    token: str
    include_current: bool = field(name="includeCurrent")


class PluginsRpcProcessingPullHistoryParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingPullHistoryParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str
    includeCurrent: bool


class PluginsRpcProcessingGetOrLoadModelParameter(
    LMStudioStruct["PluginsRpcProcessingGetOrLoadModelParameterDict"], kw_only=True
):
    pci: str
    token: str


class PluginsRpcProcessingGetOrLoadModelParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingGetOrLoadModelParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str


class PluginsRpcProcessingGetOrLoadModelReturns(
    LMStudioStruct["PluginsRpcProcessingGetOrLoadModelReturnsDict"], kw_only=True
):
    identifier: str


class PluginsRpcProcessingGetOrLoadModelReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingGetOrLoadModelReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    identifier: str


class PseudoPluginsRpcProcessingGetOrLoadModel(
    LMStudioStruct["PseudoPluginsRpcProcessingGetOrLoadModelDict"], kw_only=True
):
    parameter: PluginsRpcProcessingGetOrLoadModelParameter
    returns: PluginsRpcProcessingGetOrLoadModelReturns


class PseudoPluginsRpcProcessingGetOrLoadModelDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingGetOrLoadModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingGetOrLoadModelParameterDict
    returns: PluginsRpcProcessingGetOrLoadModelReturnsDict


class PluginsRpcProcessingHasStatusParameter(
    LMStudioStruct["PluginsRpcProcessingHasStatusParameterDict"], kw_only=True
):
    pci: str
    token: str


class PluginsRpcProcessingHasStatusParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingHasStatusParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str


PluginsRpcProcessingHasStatusReturns = bool


class PseudoPluginsRpcProcessingHasStatus(
    LMStudioStruct["PseudoPluginsRpcProcessingHasStatusDict"], kw_only=True
):
    parameter: PluginsRpcProcessingHasStatusParameter
    returns: PluginsRpcProcessingHasStatusReturns


class PseudoPluginsRpcProcessingHasStatusDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingHasStatus.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingHasStatusParameterDict
    returns: bool


class PluginsRpcProcessingNeedsNamingParameter(
    LMStudioStruct["PluginsRpcProcessingNeedsNamingParameterDict"], kw_only=True
):
    pci: str
    token: str


class PluginsRpcProcessingNeedsNamingParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingNeedsNamingParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str


PluginsRpcProcessingNeedsNamingReturns = bool


class PseudoPluginsRpcProcessingNeedsNaming(
    LMStudioStruct["PseudoPluginsRpcProcessingNeedsNamingDict"], kw_only=True
):
    parameter: PluginsRpcProcessingNeedsNamingParameter
    returns: PluginsRpcProcessingNeedsNamingReturns


class PseudoPluginsRpcProcessingNeedsNamingDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingNeedsNaming.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingNeedsNamingParameterDict
    returns: bool


class PluginsRpcProcessingSuggestNameParameter(
    LMStudioStruct["PluginsRpcProcessingSuggestNameParameterDict"], kw_only=True
):
    pci: str
    token: str
    name: str


class PluginsRpcProcessingSuggestNameParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingSuggestNameParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str
    name: str


PluginsRpcProcessingSuggestNameReturns = Any


class PseudoPluginsRpcProcessingSuggestName(
    LMStudioStruct["PseudoPluginsRpcProcessingSuggestNameDict"], kw_only=True
):
    parameter: PluginsRpcProcessingSuggestNameParameter


class PseudoPluginsRpcProcessingSuggestNameDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingSuggestName.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingSuggestNameParameterDict


class PluginsRpcProcessingSetSenderNameParameter(
    LMStudioStruct["PluginsRpcProcessingSetSenderNameParameterDict"], kw_only=True
):
    pci: str
    token: str
    name: str


class PluginsRpcProcessingSetSenderNameParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingSetSenderNameParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str
    name: str


PluginsRpcProcessingSetSenderNameReturns = Any


class PseudoPluginsRpcProcessingSetSenderName(
    LMStudioStruct["PseudoPluginsRpcProcessingSetSenderNameDict"], kw_only=True
):
    parameter: PluginsRpcProcessingSetSenderNameParameter


class PseudoPluginsRpcProcessingSetSenderNameDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingSetSenderName.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingSetSenderNameParameterDict


class PluginsRpcSetConfigSchematicsParameter(
    LMStudioStruct["PluginsRpcSetConfigSchematicsParameterDict"], kw_only=True
):
    schematics: SerializedKVConfigSchematics


class PluginsRpcSetConfigSchematicsParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcSetConfigSchematicsParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    schematics: SerializedKVConfigSchematicsDict


PluginsRpcSetConfigSchematicsReturns = Any


class PseudoPluginsRpcSetConfigSchematics(
    LMStudioStruct["PseudoPluginsRpcSetConfigSchematicsDict"], kw_only=True
):
    parameter: PluginsRpcSetConfigSchematicsParameter


class PseudoPluginsRpcSetConfigSchematicsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcSetConfigSchematics.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcSetConfigSchematicsParameterDict


class PluginsRpcSetGlobalConfigSchematicsParameter(
    LMStudioStruct["PluginsRpcSetGlobalConfigSchematicsParameterDict"], kw_only=True
):
    schematics: SerializedKVConfigSchematics


class PluginsRpcSetGlobalConfigSchematicsParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcSetGlobalConfigSchematicsParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    schematics: SerializedKVConfigSchematicsDict


PluginsRpcSetGlobalConfigSchematicsReturns = Any


class PseudoPluginsRpcSetGlobalConfigSchematics(
    LMStudioStruct["PseudoPluginsRpcSetGlobalConfigSchematicsDict"], kw_only=True
):
    parameter: PluginsRpcSetGlobalConfigSchematicsParameter


class PseudoPluginsRpcSetGlobalConfigSchematicsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcSetGlobalConfigSchematics.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcSetGlobalConfigSchematicsParameterDict


PluginsRpcPluginInitCompletedReturns = Any


class PseudoPluginsRpcPluginInitCompleted:
    pass


class RepositoryRpcSearchModelsParameter(
    LMStudioStruct["RepositoryRpcSearchModelsParameterDict"], kw_only=True
):
    opts: ModelSearchOpts


class RepositoryRpcSearchModelsParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcSearchModelsParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    opts: ModelSearchOptsDict


class RepositoryRpcGetModelDownloadOptionsReturns(
    LMStudioStruct["RepositoryRpcGetModelDownloadOptionsReturnsDict"], kw_only=True
):
    results: Sequence[ModelSearchResultDownloadOptionData]


class RepositoryRpcGetModelDownloadOptionsReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcGetModelDownloadOptionsReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    results: Sequence[ModelSearchResultDownloadOptionDataDict]


class RepositoryRpcInstallPluginDependenciesParameter(
    LMStudioStruct["RepositoryRpcInstallPluginDependenciesParameterDict"], kw_only=True
):
    plugin_folder: str = field(name="pluginFolder")


class RepositoryRpcInstallPluginDependenciesParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcInstallPluginDependenciesParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pluginFolder: str


RepositoryRpcInstallPluginDependenciesReturns = Any


class PseudoRepositoryRpcInstallPluginDependencies(
    LMStudioStruct["PseudoRepositoryRpcInstallPluginDependenciesDict"], kw_only=True
):
    parameter: RepositoryRpcInstallPluginDependenciesParameter


class PseudoRepositoryRpcInstallPluginDependenciesDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryRpcInstallPluginDependencies.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: RepositoryRpcInstallPluginDependenciesParameterDict


class RepositoryRpcGetLocalArtifactFilesParameter(
    LMStudioStruct["RepositoryRpcGetLocalArtifactFilesParameterDict"], kw_only=True
):
    path: str


class RepositoryRpcGetLocalArtifactFilesParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcGetLocalArtifactFilesParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    path: str


class RepositoryRpcGetLocalArtifactFilesReturns(
    LMStudioStruct["RepositoryRpcGetLocalArtifactFilesReturnsDict"], kw_only=True
):
    file_list: LocalArtifactFileList = field(name="fileList")


class RepositoryRpcGetLocalArtifactFilesReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcGetLocalArtifactFilesReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fileList: LocalArtifactFileListDict


class PseudoRepositoryRpcGetLocalArtifactFiles(
    LMStudioStruct["PseudoRepositoryRpcGetLocalArtifactFilesDict"], kw_only=True
):
    parameter: RepositoryRpcGetLocalArtifactFilesParameter
    returns: RepositoryRpcGetLocalArtifactFilesReturns


class PseudoRepositoryRpcGetLocalArtifactFilesDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryRpcGetLocalArtifactFiles.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: RepositoryRpcGetLocalArtifactFilesParameterDict
    returns: RepositoryRpcGetLocalArtifactFilesReturnsDict


class RepositoryRpcLoginWithPreAuthenticatedKeysParameter(
    LMStudioStruct["RepositoryRpcLoginWithPreAuthenticatedKeysParameterDict"],
    kw_only=True,
):
    key_id: str = field(name="keyId")
    public_key: str = field(name="publicKey")
    private_key: str = field(name="privateKey")


class RepositoryRpcLoginWithPreAuthenticatedKeysParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcLoginWithPreAuthenticatedKeysParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    keyId: str
    publicKey: str
    privateKey: str


class RepositoryRpcLoginWithPreAuthenticatedKeysReturns(
    LMStudioStruct["RepositoryRpcLoginWithPreAuthenticatedKeysReturnsDict"],
    kw_only=True,
):
    user_name: str = field(name="userName")


class RepositoryRpcLoginWithPreAuthenticatedKeysReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcLoginWithPreAuthenticatedKeysReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    userName: str


class PseudoRepositoryRpcLoginWithPreAuthenticatedKeys(
    LMStudioStruct["PseudoRepositoryRpcLoginWithPreAuthenticatedKeysDict"], kw_only=True
):
    parameter: RepositoryRpcLoginWithPreAuthenticatedKeysParameter
    returns: RepositoryRpcLoginWithPreAuthenticatedKeysReturns


class PseudoRepositoryRpcLoginWithPreAuthenticatedKeysDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryRpcLoginWithPreAuthenticatedKeys.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: RepositoryRpcLoginWithPreAuthenticatedKeysParameterDict
    returns: RepositoryRpcLoginWithPreAuthenticatedKeysReturnsDict


class DownloadModelChannelRequest(
    LMStudioStruct["DownloadModelChannelRequestDict"], kw_only=True
):
    download_identifier: str = field(name="downloadIdentifier")


class DownloadModelChannelRequestDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadModelCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    downloadIdentifier: str


class RepositoryChannelDownloadArtifactCreationParameter(
    LMStudioStruct["RepositoryChannelDownloadArtifactCreationParameterDict"],
    kw_only=True,
):
    artifact_owner: KebabCase = field(name="artifactOwner")
    artifact_name: KebabCaseWithDots = field(name="artifactName")
    revision_number: int | None = field(name="revisionNumber")
    path: str


class RepositoryChannelDownloadArtifactCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadArtifactCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    artifactOwner: str
    artifactName: str
    revisionNumber: NotRequired[int | None]
    path: str


class RepositoryChannelPushArtifactCreationParameter(
    LMStudioStruct["RepositoryChannelPushArtifactCreationParameterDict"], kw_only=True
):
    path: str
    description: Annotated[str, Meta(max_length=1000)] | None = None
    make_private: bool | None = field(name="makePrivate", default=None)
    write_revision: bool | None = field(name="writeRevision", default=None)
    overrides: JsonSerializable | None = None


class RepositoryChannelPushArtifactCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelPushArtifactCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    path: str
    description: NotRequired[Annotated[str, Meta(max_length=1000)] | None]
    makePrivate: NotRequired[bool | None]
    writeRevision: NotRequired[bool | None]
    overrides: NotRequired[JsonSerializable | None]


class RepositoryChannelCreateArtifactDownloadPlanCreationParameter(
    LMStudioStruct["RepositoryChannelCreateArtifactDownloadPlanCreationParameterDict"],
    kw_only=True,
):
    owner: KebabCase
    name: KebabCaseWithDots


class RepositoryChannelCreateArtifactDownloadPlanCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    owner: str
    name: str


SystemRpcNotifyReturns = Any


class SystemRpcVersionReturns(
    LMStudioStruct["SystemRpcVersionReturnsDict"], kw_only=True
):
    version: str
    build: float


class SystemRpcVersionReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for SystemRpcVersionReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    version: str
    build: float


class PseudoSystemRpcVersion(
    LMStudioStruct["PseudoSystemRpcVersionDict"], kw_only=True
):
    returns: SystemRpcVersionReturns


class PseudoSystemRpcVersionDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoSystemRpcVersion.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    returns: SystemRpcVersionReturnsDict


class SystemRpcSetExperimentFlagParameter(
    LMStudioStruct["SystemRpcSetExperimentFlagParameterDict"], kw_only=True
):
    code: str
    value: bool


class SystemRpcSetExperimentFlagParameterDict(TypedDict):
    """Corresponding typed dictionary definition for SystemRpcSetExperimentFlagParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: str
    value: bool


SystemRpcSetExperimentFlagReturns = Any


class PseudoSystemRpcSetExperimentFlag(
    LMStudioStruct["PseudoSystemRpcSetExperimentFlagDict"], kw_only=True
):
    parameter: SystemRpcSetExperimentFlagParameter


class PseudoSystemRpcSetExperimentFlagDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoSystemRpcSetExperimentFlag.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: SystemRpcSetExperimentFlagParameterDict


SystemRpcGetExperimentFlagsReturns = Sequence[str]


class PseudoSystemRpcGetExperimentFlags(
    LMStudioStruct["PseudoSystemRpcGetExperimentFlagsDict"], kw_only=True
):
    returns: SystemRpcGetExperimentFlagsReturns


class PseudoSystemRpcGetExperimentFlagsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoSystemRpcGetExperimentFlags.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    returns: SystemRpcGetExperimentFlagsReturns


class PseudoSystemChannelAlive:
    pass


class ToolResultMessage(
    LMStudioStruct["ToolResultMessageDict"], kw_only=True, tag_field="role", tag="tool"
):
    role: ClassVar[Annotated[Literal["tool"], Meta(title="Role")]] = "tool"
    content: Sequence[ToolCallResultData]


class ToolResultMessageDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessageDataTool.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    role: Literal["tool"]
    content: Sequence[ToolCallResultDataDict]


class DiagnosticsLogEventDataLlmPredictionInput(
    LMStudioStruct["DiagnosticsLogEventDataLlmPredictionInputDict"], kw_only=True
):
    type: Annotated[Literal["llm.prediction.input"], Meta(title="Type")]
    model_path: str = field(name="modelPath")
    model_identifier: str = field(name="modelIdentifier")
    input: str


class DiagnosticsLogEventDataLlmPredictionInputDict(TypedDict):
    """Corresponding typed dictionary definition for DiagnosticsLogEventDataLlmPredictionInput.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["llm.prediction.input"], Meta(title="Type")]
    modelPath: str
    modelIdentifier: str
    input: str


class ErrorDisplayDataGenericSpecificModelUnloaded(
    LMStudioStruct["ErrorDisplayDataGenericSpecificModelUnloadedDict"],
    kw_only=True,
    tag_field="code",
    tag="generic.specificModelUnloaded",
):
    code: ClassVar[
        Annotated[Literal["generic.specificModelUnloaded"], Meta(title="Code")]
    ] = "generic.specificModelUnloaded"


class ErrorDisplayDataGenericSpecificModelUnloadedDict(TypedDict):
    """Corresponding typed dictionary definition for ErrorDisplayDataGenericSpecificModelUnloaded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: Literal["generic.specificModelUnloaded"]


class ErrorDisplayDataGenericPathNotFound(
    LMStudioStruct["ErrorDisplayDataGenericPathNotFoundDict"],
    kw_only=True,
    tag_field="code",
    tag="generic.pathNotFound",
):
    code: ClassVar[Annotated[Literal["generic.pathNotFound"], Meta(title="Code")]] = (
        "generic.pathNotFound"
    )
    path: str
    available_paths_sample: Sequence[str] = field(name="availablePathsSample")
    total_models: int = field(name="totalModels")


class ErrorDisplayDataGenericPathNotFoundDict(TypedDict):
    """Corresponding typed dictionary definition for ErrorDisplayDataGenericPathNotFound.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: Literal["generic.pathNotFound"]
    path: str
    availablePathsSample: Sequence[str]
    totalModels: int


class ErrorDisplayDataGenericIdentifierNotFound(
    LMStudioStruct["ErrorDisplayDataGenericIdentifierNotFoundDict"],
    kw_only=True,
    tag_field="code",
    tag="generic.identifierNotFound",
):
    code: ClassVar[
        Annotated[Literal["generic.identifierNotFound"], Meta(title="Code")]
    ] = "generic.identifierNotFound"
    identifier: str
    loaded_models_sample: Sequence[str] = field(name="loadedModelsSample")
    total_loaded_models: int = field(name="totalLoadedModels")


class ErrorDisplayDataGenericIdentifierNotFoundDict(TypedDict):
    """Corresponding typed dictionary definition for ErrorDisplayDataGenericIdentifierNotFound.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: Literal["generic.identifierNotFound"]
    identifier: str
    loadedModelsSample: Sequence[str]
    totalLoadedModels: int


class ErrorDisplayDataGenericDomainMismatch(
    LMStudioStruct["ErrorDisplayDataGenericDomainMismatchDict"],
    kw_only=True,
    tag_field="code",
    tag="generic.domainMismatch",
):
    code: ClassVar[Annotated[Literal["generic.domainMismatch"], Meta(title="Code")]] = (
        "generic.domainMismatch"
    )
    path: str
    actual_domain: ModelDomainType = field(name="actualDomain")
    expected_domain: ModelDomainType = field(name="expectedDomain")


class ErrorDisplayDataGenericDomainMismatchDict(TypedDict):
    """Corresponding typed dictionary definition for ErrorDisplayDataGenericDomainMismatch.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: Literal["generic.domainMismatch"]
    path: str
    actualDomain: ModelDomainType
    expectedDomain: ModelDomainType


class ErrorDisplayDataGenericEngineDoesNotSupportFeature(
    LMStudioStruct["ErrorDisplayDataGenericEngineDoesNotSupportFeatureDict"],
    kw_only=True,
    tag_field="code",
    tag="generic.engineDoesNotSupportFeature",
):
    code: ClassVar[
        Annotated[Literal["generic.engineDoesNotSupportFeature"], Meta(title="Code")]
    ] = "generic.engineDoesNotSupportFeature"
    feature: str
    engine_name: str = field(name="engineName")
    engine_type: str = field(name="engineType")
    installed_version: str = field(name="installedVersion")
    supported_version: str | None = field(name="supportedVersion")


class ErrorDisplayDataGenericEngineDoesNotSupportFeatureDict(TypedDict):
    """Corresponding typed dictionary definition for ErrorDisplayDataGenericEngineDoesNotSupportFeature.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: Literal["generic.engineDoesNotSupportFeature"]
    feature: str
    engineName: str
    engineType: str
    installedVersion: str
    supportedVersion: NotRequired[str | None]


class AvailablePresetsSampleItem(
    LMStudioStruct["AvailablePresetsSampleItemDict"], kw_only=True
):
    identifier: str
    name: str


class AvailablePresetsSampleItemDict(TypedDict):
    """Corresponding typed dictionary definition for AvailablePresetsSampleItem.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    identifier: str
    name: str


class ErrorDisplayDataGenericPresetNotFound(
    LMStudioStruct["ErrorDisplayDataGenericPresetNotFoundDict"],
    kw_only=True,
    tag_field="code",
    tag="generic.presetNotFound",
):
    code: ClassVar[Annotated[Literal["generic.presetNotFound"], Meta(title="Code")]] = (
        "generic.presetNotFound"
    )
    specified_fuzzy_preset_identifier: str = field(
        name="specifiedFuzzyPresetIdentifier"
    )
    available_presets_sample: Sequence[AvailablePresetsSampleItem] = field(
        name="availablePresetsSample"
    )
    total_available_presets: int = field(name="totalAvailablePresets")


class ErrorDisplayDataGenericPresetNotFoundDict(TypedDict):
    """Corresponding typed dictionary definition for ErrorDisplayDataGenericPresetNotFound.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: Literal["generic.presetNotFound"]
    specifiedFuzzyPresetIdentifier: str
    availablePresetsSample: Sequence[AvailablePresetsSampleItemDict]
    totalAvailablePresets: int


class ParsedFileIdentifierLocal(
    LMStudioStruct["ParsedFileIdentifierLocalDict"],
    kw_only=True,
    tag_field="type",
    tag="local",
):
    type: ClassVar[Annotated[Literal["local"], Meta(title="Type")]] = "local"
    file_name: str = field(name="fileName")


class ParsedFileIdentifierLocalDict(TypedDict):
    """Corresponding typed dictionary definition for ParsedFileIdentifierLocal.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["local"]
    fileName: str


class ParsedFileIdentifierBase64(
    LMStudioStruct["ParsedFileIdentifierBase64Dict"],
    kw_only=True,
    tag_field="type",
    tag="base64",
):
    type: ClassVar[Annotated[Literal["base64"], Meta(title="Type")]] = "base64"
    base64_data: str = field(name="base64Data")


class ParsedFileIdentifierBase64Dict(TypedDict):
    """Corresponding typed dictionary definition for ParsedFileIdentifierBase64.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["base64"]
    base64Data: str


class KvConfigFieldDependencyConditionEquals(
    LMStudioStruct["KvConfigFieldDependencyConditionEqualsDict"],
    kw_only=True,
    tag_field="type",
    tag="equals",
):
    type: ClassVar[Annotated[Literal["equals"], Meta(title="Type")]] = "equals"
    value: Any | None = None


class KvConfigFieldDependencyConditionEqualsDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfigFieldDependencyConditionEquals.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["equals"]
    value: NotRequired[Any | None]


class KvConfigFieldDependencyConditionNotEquals(
    LMStudioStruct["KvConfigFieldDependencyConditionNotEqualsDict"],
    kw_only=True,
    tag_field="type",
    tag="notEquals",
):
    type: ClassVar[Annotated[Literal["notEquals"], Meta(title="Type")]] = "notEquals"
    value: Any | None = None


class KvConfigFieldDependencyConditionNotEqualsDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfigFieldDependencyConditionNotEquals.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["notEquals"]
    value: NotRequired[Any | None]


class ContentBlockStyleDefault(
    LMStudioStruct["ContentBlockStyleDefaultDict"],
    kw_only=True,
    tag_field="type",
    tag="default",
):
    type: ClassVar[Annotated[Literal["default"], Meta(title="Type")]] = "default"


class ContentBlockStyleDefaultDict(TypedDict):
    """Corresponding typed dictionary definition for ContentBlockStyleDefault.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["default"]


class ContentBlockStyleCustomLabel(
    LMStudioStruct["ContentBlockStyleCustomLabelDict"],
    kw_only=True,
    tag_field="type",
    tag="customLabel",
):
    type: ClassVar[Annotated[Literal["customLabel"], Meta(title="Type")]] = (
        "customLabel"
    )
    label: str
    color: ColorPalette | None = None


class ContentBlockStyleCustomLabelDict(TypedDict):
    """Corresponding typed dictionary definition for ContentBlockStyleCustomLabel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["customLabel"]
    label: str
    color: NotRequired[ColorPalette | None]


class ContentBlockStyleThinking(
    LMStudioStruct["ContentBlockStyleThinkingDict"],
    kw_only=True,
    tag_field="type",
    tag="thinking",
):
    type: ClassVar[Annotated[Literal["thinking"], Meta(title="Type")]] = "thinking"
    ended: bool | None = None
    title: str | None = None


class ContentBlockStyleThinkingDict(TypedDict):
    """Corresponding typed dictionary definition for ContentBlockStyleThinking.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["thinking"]
    ended: NotRequired[bool | None]
    title: NotRequired[str | None]


class LlmContextReferenceJsonFile(
    LMStudioStruct["LlmContextReferenceJsonFileDict"],
    kw_only=True,
    tag_field="type",
    tag="jsonFile",
):
    type: ClassVar[Annotated[Literal["jsonFile"], Meta(title="Type")]] = "jsonFile"
    abs_path: str = field(name="absPath")


class LlmContextReferenceJsonFileDict(TypedDict):
    """Corresponding typed dictionary definition for LlmContextReferenceJsonFile.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["jsonFile"]
    absPath: str


class LlmContextReferenceYamlFile(
    LMStudioStruct["LlmContextReferenceYamlFileDict"],
    kw_only=True,
    tag_field="type",
    tag="yamlFile",
):
    type: ClassVar[Annotated[Literal["yamlFile"], Meta(title="Type")]] = "yamlFile"
    abs_path: str = field(name="absPath")


class LlmContextReferenceYamlFileDict(TypedDict):
    """Corresponding typed dictionary definition for LlmContextReferenceYamlFile.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["yamlFile"]
    absPath: str


class LlmToolParametersObject(
    LMStudioStruct["LlmToolParametersObjectDict"], kw_only=True
):
    type: Annotated[Literal["object"], Meta(title="Type")]
    properties: Mapping[str, JsonSerializable]
    required: Sequence[str] | None = None
    additional_properties: bool | None = field(
        name="additionalProperties", default=None
    )


class LlmToolParametersObjectDict(TypedDict):
    """Corresponding typed dictionary definition for LlmToolParametersObject.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["object"], Meta(title="Type")]
    properties: Mapping[str, JsonSerializable]
    required: NotRequired[Sequence[str] | None]
    additionalProperties: NotRequired[bool | None]


class LlmToolUseSettingNone(
    LMStudioStruct["LlmToolUseSettingNoneDict"],
    kw_only=True,
    tag_field="type",
    tag="none",
):
    type: ClassVar[Annotated[Literal["none"], Meta(title="Type")]] = "none"


class LlmToolUseSettingNoneDict(TypedDict):
    """Corresponding typed dictionary definition for LlmToolUseSettingNone.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["none"]


class ProcessingRequestResponseConfirmToolCallResultAllow(
    LMStudioStruct["ProcessingRequestResponseConfirmToolCallResultAllowDict"],
    kw_only=True,
    tag_field="type",
    tag="allow",
):
    type: ClassVar[Annotated[Literal["allow"], Meta(title="Type")]] = "allow"
    tool_args_override: Mapping[str, Any] | None = field(
        name="toolArgsOverride", default=None
    )


class ProcessingRequestResponseConfirmToolCallResultAllowDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingRequestResponseConfirmToolCallResultAllow.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["allow"]
    toolArgsOverride: NotRequired[Mapping[str, Any] | None]


class ProcessingRequestResponseConfirmToolCallResultDeny(
    LMStudioStruct["ProcessingRequestResponseConfirmToolCallResultDenyDict"],
    kw_only=True,
    tag_field="type",
    tag="deny",
):
    type: ClassVar[Annotated[Literal["deny"], Meta(title="Type")]] = "deny"
    deny_reason: str | None = field(name="denyReason", default=None)


class ProcessingRequestResponseConfirmToolCallResultDenyDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingRequestResponseConfirmToolCallResultDeny.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["deny"]
    denyReason: NotRequired[str | None]


class BlockLocationBeforeId(
    LMStudioStruct["BlockLocationBeforeIdDict"],
    kw_only=True,
    tag_field="type",
    tag="beforeId",
):
    type: ClassVar[Annotated[Literal["beforeId"], Meta(title="Type")]] = "beforeId"
    id: str


class BlockLocationBeforeIdDict(TypedDict):
    """Corresponding typed dictionary definition for BlockLocationBeforeId.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["beforeId"]
    id: str


class BlockLocationAfterId(
    LMStudioStruct["BlockLocationAfterIdDict"],
    kw_only=True,
    tag_field="type",
    tag="afterId",
):
    type: ClassVar[Annotated[Literal["afterId"], Meta(title="Type")]] = "afterId"
    id: str


class BlockLocationAfterIdDict(TypedDict):
    """Corresponding typed dictionary definition for BlockLocationAfterId.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["afterId"]
    id: str


class ToolStatusStepStateStatusGeneratingToolCall(
    LMStudioStruct["ToolStatusStepStateStatusGeneratingToolCallDict"],
    kw_only=True,
    tag_field="type",
    tag="generatingToolCall",
):
    type: ClassVar[Annotated[Literal["generatingToolCall"], Meta(title="Type")]] = (
        "generatingToolCall"
    )
    name: str | None = None
    plugin_identifier: str | None = field(name="pluginIdentifier", default=None)
    arguments_string: str | None = field(name="argumentsString", default=None)


class ToolStatusStepStateStatusGeneratingToolCallDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusGeneratingToolCall.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["generatingToolCall"]
    name: NotRequired[str | None]
    pluginIdentifier: NotRequired[str | None]
    argumentsString: NotRequired[str | None]


class ToolStatusStepStateStatusToolCallGenerationFailed(
    LMStudioStruct["ToolStatusStepStateStatusToolCallGenerationFailedDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationFailed",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationFailed"], Meta(title="Type")]
    ] = "toolCallGenerationFailed"
    error: str
    raw_content: str | None = field(name="rawContent", default=None)


class ToolStatusStepStateStatusToolCallGenerationFailedDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusToolCallGenerationFailed.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationFailed"]
    error: str
    rawContent: NotRequired[str | None]


class ToolStatusStepStateStatusToolCallQueued(
    LMStudioStruct["ToolStatusStepStateStatusToolCallQueuedDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallQueued",
):
    type: ClassVar[Annotated[Literal["toolCallQueued"], Meta(title="Type")]] = (
        "toolCallQueued"
    )


class ToolStatusStepStateStatusToolCallQueuedDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusToolCallQueued.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallQueued"]


class ToolStatusStepStateStatusConfirmingToolCall(
    LMStudioStruct["ToolStatusStepStateStatusConfirmingToolCallDict"],
    kw_only=True,
    tag_field="type",
    tag="confirmingToolCall",
):
    type: ClassVar[Annotated[Literal["confirmingToolCall"], Meta(title="Type")]] = (
        "confirmingToolCall"
    )


class ToolStatusStepStateStatusConfirmingToolCallDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusConfirmingToolCall.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["confirmingToolCall"]


class ToolStatusStepStateStatusToolCallDenied(
    LMStudioStruct["ToolStatusStepStateStatusToolCallDeniedDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallDenied",
):
    type: ClassVar[Annotated[Literal["toolCallDenied"], Meta(title="Type")]] = (
        "toolCallDenied"
    )
    deny_reason: str | None = field(name="denyReason", default=None)


class ToolStatusStepStateStatusToolCallDeniedDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusToolCallDenied.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallDenied"]
    denyReason: NotRequired[str | None]


class ToolStatusStepStateStatusCallingTool(
    LMStudioStruct["ToolStatusStepStateStatusCallingToolDict"],
    kw_only=True,
    tag_field="type",
    tag="callingTool",
):
    type: ClassVar[Annotated[Literal["callingTool"], Meta(title="Type")]] = (
        "callingTool"
    )


class ToolStatusStepStateStatusCallingToolDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusCallingTool.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["callingTool"]


class ToolStatusStepStateStatusToolCallFailed(
    LMStudioStruct["ToolStatusStepStateStatusToolCallFailedDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallFailed",
):
    type: ClassVar[Annotated[Literal["toolCallFailed"], Meta(title="Type")]] = (
        "toolCallFailed"
    )
    error: str


class ToolStatusStepStateStatusToolCallFailedDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusToolCallFailed.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallFailed"]
    error: str


class ToolStatusStepStateStatusToolCallSucceeded(
    LMStudioStruct["ToolStatusStepStateStatusToolCallSucceededDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallSucceeded",
):
    type: ClassVar[Annotated[Literal["toolCallSucceeded"], Meta(title="Type")]] = (
        "toolCallSucceeded"
    )
    time_ms: int = field(name="timeMs")


class ToolStatusStepStateStatusToolCallSucceededDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepStateStatusToolCallSucceeded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallSucceeded"]
    timeMs: int


class ModelSpecifierInstanceReference(
    LMStudioStruct["ModelSpecifierInstanceReferenceDict"],
    kw_only=True,
    tag_field="type",
    tag="instanceReference",
):
    type: ClassVar[Annotated[Literal["instanceReference"], Meta(title="Type")]] = (
        "instanceReference"
    )
    instance_reference: str = field(name="instanceReference")


class ModelSpecifierInstanceReferenceDict(TypedDict):
    """Corresponding typed dictionary definition for ModelSpecifierInstanceReference.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["instanceReference"]
    instanceReference: str


class ArtifactDownloadPlanNodeArtifact(
    LMStudioStruct["ArtifactDownloadPlanNodeArtifactDict"],
    kw_only=True,
    tag_field="type",
    tag="artifact",
):
    type: ClassVar[Annotated[Literal["artifact"], Meta(title="Type")]] = "artifact"
    owner: KebabCase
    name: KebabCaseWithDots
    state: ArtifactDownloadPlanNodeState
    dependency_nodes: Sequence[int] = field(name="dependencyNodes")
    artifact_type: ArtifactType | None = field(name="artifactType", default=None)
    size_bytes: int | None = field(name="sizeBytes", default=None)


class ArtifactDownloadPlanNodeArtifactDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactDownloadPlanNodeArtifact.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["artifact"]
    owner: str
    name: str
    state: ArtifactDownloadPlanNodeState
    dependencyNodes: Sequence[int]
    artifactType: NotRequired[ArtifactType | None]
    sizeBytes: NotRequired[int | None]


class ArtifactDownloadPlanNodeModel(
    LMStudioStruct["ArtifactDownloadPlanNodeModelDict"],
    kw_only=True,
    tag_field="type",
    tag="model",
):
    type: ClassVar[Annotated[Literal["model"], Meta(title="Type")]] = "model"
    state: ArtifactDownloadPlanNodeState
    resolved_sources: int | None = field(name="resolvedSources", default=None)
    total_sources: int | None = field(name="totalSources", default=None)
    already_owned: ArtifactDownloadPlanModelInfo | None = field(
        name="alreadyOwned", default=None
    )
    selected: ArtifactDownloadPlanModelInfo | None = None


class ArtifactDownloadPlanNodeModelDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactDownloadPlanNodeModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["model"]
    state: ArtifactDownloadPlanNodeState
    resolvedSources: NotRequired[int | None]
    totalSources: NotRequired[int | None]
    alreadyOwned: NotRequired[ArtifactDownloadPlanModelInfoDict | None]
    selected: NotRequired[ArtifactDownloadPlanModelInfoDict | None]


class ModelSearchResultIdentifierCatalog(
    LMStudioStruct["ModelSearchResultIdentifierCatalogDict"],
    kw_only=True,
    tag_field="type",
    tag="catalog",
):
    type: ClassVar[Annotated[Literal["catalog"], Meta(title="Type")]] = "catalog"
    identifier: str


class ModelSearchResultIdentifierCatalogDict(TypedDict):
    """Corresponding typed dictionary definition for ModelSearchResultIdentifierCatalog.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["catalog"]
    identifier: str


class ModelSearchResultIdentifierHf(
    LMStudioStruct["ModelSearchResultIdentifierHfDict"],
    kw_only=True,
    tag_field="type",
    tag="hf",
):
    type: ClassVar[Annotated[Literal["hf"], Meta(title="Type")]] = "hf"
    identifier: str


class ModelSearchResultIdentifierHfDict(TypedDict):
    """Corresponding typed dictionary definition for ModelSearchResultIdentifierHf.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["hf"]
    identifier: str


class RetrievalChunkingMethodRecursiveV1(
    LMStudioStruct["RetrievalChunkingMethodRecursiveV1Dict"], kw_only=True
):
    type: Annotated[Literal["recursive-v1"], Meta(title="Type")]
    chunk_size: int = field(name="chunkSize")
    chunk_overlap: int = field(name="chunkOverlap")


class RetrievalChunkingMethodRecursiveV1Dict(TypedDict):
    """Corresponding typed dictionary definition for RetrievalChunkingMethodRecursiveV1.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["recursive-v1"], Meta(title="Type")]
    chunkSize: int
    chunkOverlap: int


VirtualModelBooleanCustomFieldDefinitionEffectsItem = (
    VirtualModelCustomFieldSetJinjaVariableEffect
    | VirtualModelCustomFieldPrependSystemPromptEffect
    | VirtualModelCustomFieldAppendSystemPromptEffect
)
VirtualModelBooleanCustomFieldDefinitionEffectsItemDict = (
    VirtualModelCustomFieldAppendSystemPromptEffectDict
    | VirtualModelCustomFieldSetJinjaVariableEffectDict
    | VirtualModelCustomFieldPrependSystemPromptEffectDict
)
VirtualModelStringCustomFieldDefinitionEffectsItem = (
    VirtualModelCustomFieldSetJinjaVariableEffect
)


class DiagnosticsChannelStreamLogsToServerPacketStop(
    LMStudioStruct["DiagnosticsChannelStreamLogsToServerPacketStopDict"], kw_only=True
):
    type: Annotated[Literal["stop"], Meta(title="Type")]


class DiagnosticsChannelStreamLogsToServerPacketStopDict(TypedDict):
    """Corresponding typed dictionary definition for DiagnosticsChannelStreamLogsToServerPacketStop.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["stop"], Meta(title="Type")]


class EmbeddingChannelLoadModelToClientPacketProgress(
    LMStudioStruct["EmbeddingChannelLoadModelToClientPacketProgressDict"],
    kw_only=True,
    tag_field="type",
    tag="progress",
):
    type: ClassVar[Annotated[Literal["progress"], Meta(title="Type")]] = "progress"
    progress: float


class EmbeddingChannelLoadModelToClientPacketProgressDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelLoadModelToClientPacketProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["progress"]
    progress: float


class EmbeddingChannelLoadModelToServerPacketCancel(
    LMStudioStruct["EmbeddingChannelLoadModelToServerPacketCancelDict"], kw_only=True
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class EmbeddingChannelLoadModelToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelLoadModelToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class EmbeddingChannelGetOrLoadToClientPacketLoadProgress(
    LMStudioStruct["EmbeddingChannelGetOrLoadToClientPacketLoadProgressDict"],
    kw_only=True,
    tag_field="type",
    tag="loadProgress",
):
    type: ClassVar[Annotated[Literal["loadProgress"], Meta(title="Type")]] = (
        "loadProgress"
    )
    progress: float


class EmbeddingChannelGetOrLoadToClientPacketLoadProgressDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelGetOrLoadToClientPacketLoadProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["loadProgress"]
    progress: float


class EmbeddingChannelGetOrLoadToServerPacketCancel(
    LMStudioStruct["EmbeddingChannelGetOrLoadToServerPacketCancelDict"], kw_only=True
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class EmbeddingChannelGetOrLoadToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelGetOrLoadToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class FilesChannelRetrieveToClientPacketOnFileProcessList(
    LMStudioStruct["FilesChannelRetrieveToClientPacketOnFileProcessListDict"],
    kw_only=True,
    tag_field="type",
    tag="onFileProcessList",
):
    type: ClassVar[Annotated[Literal["onFileProcessList"], Meta(title="Type")]] = (
        "onFileProcessList"
    )
    indices: Sequence[int]


class FilesChannelRetrieveToClientPacketOnFileProcessListDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnFileProcessList.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onFileProcessList"]
    indices: Sequence[int]


class FilesChannelRetrieveToClientPacketOnFileProcessingStart(
    LMStudioStruct["FilesChannelRetrieveToClientPacketOnFileProcessingStartDict"],
    kw_only=True,
    tag_field="type",
    tag="onFileProcessingStart",
):
    type: ClassVar[Annotated[Literal["onFileProcessingStart"], Meta(title="Type")]] = (
        "onFileProcessingStart"
    )
    index: int


class FilesChannelRetrieveToClientPacketOnFileProcessingStartDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnFileProcessingStart.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onFileProcessingStart"]
    index: int


class FilesChannelRetrieveToClientPacketOnFileProcessingEnd(
    LMStudioStruct["FilesChannelRetrieveToClientPacketOnFileProcessingEndDict"],
    kw_only=True,
    tag_field="type",
    tag="onFileProcessingEnd",
):
    type: ClassVar[Annotated[Literal["onFileProcessingEnd"], Meta(title="Type")]] = (
        "onFileProcessingEnd"
    )
    index: int


class FilesChannelRetrieveToClientPacketOnFileProcessingEndDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnFileProcessingEnd.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onFileProcessingEnd"]
    index: int


class FilesChannelRetrieveToClientPacketOnFileProcessingStepStart(
    LMStudioStruct["FilesChannelRetrieveToClientPacketOnFileProcessingStepStartDict"],
    kw_only=True,
    tag_field="type",
    tag="onFileProcessingStepStart",
):
    type: ClassVar[
        Annotated[Literal["onFileProcessingStepStart"], Meta(title="Type")]
    ] = "onFileProcessingStepStart"
    index: int
    step: RetrievalFileProcessingStep


class FilesChannelRetrieveToClientPacketOnFileProcessingStepStartDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnFileProcessingStepStart.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onFileProcessingStepStart"]
    index: int
    step: RetrievalFileProcessingStep


class FilesChannelRetrieveToClientPacketOnFileProcessingStepProgress(
    LMStudioStruct[
        "FilesChannelRetrieveToClientPacketOnFileProcessingStepProgressDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="onFileProcessingStepProgress",
):
    type: ClassVar[
        Annotated[Literal["onFileProcessingStepProgress"], Meta(title="Type")]
    ] = "onFileProcessingStepProgress"
    index: int
    step: RetrievalFileProcessingStep
    progress: float


class FilesChannelRetrieveToClientPacketOnFileProcessingStepProgressDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnFileProcessingStepProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onFileProcessingStepProgress"]
    index: int
    step: RetrievalFileProcessingStep
    progress: float


class FilesChannelRetrieveToClientPacketOnFileProcessingStepEnd(
    LMStudioStruct["FilesChannelRetrieveToClientPacketOnFileProcessingStepEndDict"],
    kw_only=True,
    tag_field="type",
    tag="onFileProcessingStepEnd",
):
    type: ClassVar[
        Annotated[Literal["onFileProcessingStepEnd"], Meta(title="Type")]
    ] = "onFileProcessingStepEnd"
    index: int
    step: RetrievalFileProcessingStep


class FilesChannelRetrieveToClientPacketOnFileProcessingStepEndDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnFileProcessingStepEnd.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onFileProcessingStepEnd"]
    index: int
    step: RetrievalFileProcessingStep


class FilesChannelRetrieveToClientPacketOnSearchingStart(
    LMStudioStruct["FilesChannelRetrieveToClientPacketOnSearchingStartDict"],
    kw_only=True,
    tag_field="type",
    tag="onSearchingStart",
):
    type: ClassVar[Annotated[Literal["onSearchingStart"], Meta(title="Type")]] = (
        "onSearchingStart"
    )


class FilesChannelRetrieveToClientPacketOnSearchingStartDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnSearchingStart.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onSearchingStart"]


class FilesChannelRetrieveToClientPacketOnSearchingEnd(
    LMStudioStruct["FilesChannelRetrieveToClientPacketOnSearchingEndDict"],
    kw_only=True,
    tag_field="type",
    tag="onSearchingEnd",
):
    type: ClassVar[Annotated[Literal["onSearchingEnd"], Meta(title="Type")]] = (
        "onSearchingEnd"
    )


class FilesChannelRetrieveToClientPacketOnSearchingEndDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketOnSearchingEnd.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["onSearchingEnd"]


class FilesChannelRetrieveToClientPacketResult(
    LMStudioStruct["FilesChannelRetrieveToClientPacketResultDict"],
    kw_only=True,
    tag_field="type",
    tag="result",
):
    type: ClassVar[Annotated[Literal["result"], Meta(title="Type")]] = "result"
    result: InternalRetrievalResult


class FilesChannelRetrieveToClientPacketResultDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToClientPacketResult.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["result"]
    result: InternalRetrievalResultDict


class FilesChannelRetrieveToServerPacketStop(
    LMStudioStruct["FilesChannelRetrieveToServerPacketStopDict"], kw_only=True
):
    type: Annotated[Literal["stop"], Meta(title="Type")]


class FilesChannelRetrieveToServerPacketStopDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveToServerPacketStop.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["stop"], Meta(title="Type")]


class FilesChannelParseDocumentToClientPacketParserLoaded(
    LMStudioStruct["FilesChannelParseDocumentToClientPacketParserLoadedDict"],
    kw_only=True,
    tag_field="type",
    tag="parserLoaded",
):
    type: ClassVar[Annotated[Literal["parserLoaded"], Meta(title="Type")]] = (
        "parserLoaded"
    )
    parser: DocumentParsingLibraryIdentifier


class FilesChannelParseDocumentToClientPacketParserLoadedDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelParseDocumentToClientPacketParserLoaded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["parserLoaded"]
    parser: DocumentParsingLibraryIdentifierDict


class FilesChannelParseDocumentToClientPacketProgress(
    LMStudioStruct["FilesChannelParseDocumentToClientPacketProgressDict"],
    kw_only=True,
    tag_field="type",
    tag="progress",
):
    type: ClassVar[Annotated[Literal["progress"], Meta(title="Type")]] = "progress"
    progress: float


class FilesChannelParseDocumentToClientPacketProgressDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelParseDocumentToClientPacketProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["progress"]
    progress: float


class FilesChannelParseDocumentToClientPacketResult(
    LMStudioStruct["FilesChannelParseDocumentToClientPacketResultDict"],
    kw_only=True,
    tag_field="type",
    tag="result",
):
    type: ClassVar[Annotated[Literal["result"], Meta(title="Type")]] = "result"
    content: str
    parser: DocumentParsingLibraryIdentifier


class FilesChannelParseDocumentToClientPacketResultDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelParseDocumentToClientPacketResult.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["result"]
    content: str
    parser: DocumentParsingLibraryIdentifierDict


class FilesChannelParseDocumentToServerPacketCancel(
    LMStudioStruct["FilesChannelParseDocumentToServerPacketCancelDict"], kw_only=True
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class FilesChannelParseDocumentToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelParseDocumentToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class LlmChannelLoadModelToClientPacketProgress(
    LMStudioStruct["LlmChannelLoadModelToClientPacketProgressDict"],
    kw_only=True,
    tag_field="type",
    tag="progress",
):
    type: ClassVar[Annotated[Literal["progress"], Meta(title="Type")]] = "progress"
    progress: float


class LlmChannelLoadModelToClientPacketProgressDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelLoadModelToClientPacketProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["progress"]
    progress: float


class LlmChannelLoadModelToServerPacketCancel(
    LMStudioStruct["LlmChannelLoadModelToServerPacketCancelDict"], kw_only=True
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class LlmChannelLoadModelToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelLoadModelToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class LlmChannelGetOrLoadToClientPacketLoadProgress(
    LMStudioStruct["LlmChannelGetOrLoadToClientPacketLoadProgressDict"],
    kw_only=True,
    tag_field="type",
    tag="loadProgress",
):
    type: ClassVar[Annotated[Literal["loadProgress"], Meta(title="Type")]] = (
        "loadProgress"
    )
    progress: float


class LlmChannelGetOrLoadToClientPacketLoadProgressDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGetOrLoadToClientPacketLoadProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["loadProgress"]
    progress: float


class LlmChannelGetOrLoadToServerPacketCancel(
    LMStudioStruct["LlmChannelGetOrLoadToServerPacketCancelDict"], kw_only=True
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class LlmChannelGetOrLoadToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGetOrLoadToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class Logprob(LMStudioStruct["LogprobDict"], kw_only=True):
    text: str
    logprob: float


class LogprobDict(TypedDict):
    """Corresponding typed dictionary definition for Logprob.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    text: str
    logprob: float


class LlmChannelPredictToClientPacketFragment(
    LMStudioStruct["LlmChannelPredictToClientPacketFragmentDict"],
    kw_only=True,
    tag_field="type",
    tag="fragment",
):
    type: ClassVar[Annotated[Literal["fragment"], Meta(title="Type")]] = "fragment"
    fragment: LlmPredictionFragment
    logprobs: Sequence[Sequence[Logprob]] | None = None


class LlmChannelPredictToClientPacketFragmentDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketFragment.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["fragment"]
    fragment: LlmPredictionFragmentDict
    logprobs: NotRequired[Sequence[Sequence[LogprobDict]] | None]


class LlmChannelPredictToClientPacketPromptProcessingProgress(
    LMStudioStruct["LlmChannelPredictToClientPacketPromptProcessingProgressDict"],
    kw_only=True,
    tag_field="type",
    tag="promptProcessingProgress",
):
    type: ClassVar[
        Annotated[Literal["promptProcessingProgress"], Meta(title="Type")]
    ] = "promptProcessingProgress"
    progress: float


class LlmChannelPredictToClientPacketPromptProcessingProgressDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketPromptProcessingProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["promptProcessingProgress"]
    progress: float


class LlmChannelPredictToClientPacketToolCallGenerationStart(
    LMStudioStruct["LlmChannelPredictToClientPacketToolCallGenerationStartDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationStart",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationStart"], Meta(title="Type")]
    ] = "toolCallGenerationStart"


class LlmChannelPredictToClientPacketToolCallGenerationStartDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketToolCallGenerationStart.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationStart"]


class LlmChannelPredictToClientPacketToolCallGenerationNameReceived(
    LMStudioStruct["LlmChannelPredictToClientPacketToolCallGenerationNameReceivedDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationNameReceived",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationNameReceived"], Meta(title="Type")]
    ] = "toolCallGenerationNameReceived"
    name: str


class LlmChannelPredictToClientPacketToolCallGenerationNameReceivedDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketToolCallGenerationNameReceived.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationNameReceived"]
    name: str


class LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGenerated(
    LMStudioStruct[
        "LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGeneratedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationArgumentFragmentGenerated",
):
    type: ClassVar[
        Annotated[
            Literal["toolCallGenerationArgumentFragmentGenerated"], Meta(title="Type")
        ]
    ] = "toolCallGenerationArgumentFragmentGenerated"
    content: str


class LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGeneratedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGenerated.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationArgumentFragmentGenerated"]
    content: str


class LlmChannelPredictToClientPacketToolCallGenerationFailed(
    LMStudioStruct["LlmChannelPredictToClientPacketToolCallGenerationFailedDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationFailed",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationFailed"], Meta(title="Type")]
    ] = "toolCallGenerationFailed"
    error: SerializedLMSExtendedError
    raw_content: str | None = field(name="rawContent", default=None)


class LlmChannelPredictToClientPacketToolCallGenerationFailedDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketToolCallGenerationFailed.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationFailed"]
    error: SerializedLMSExtendedErrorDict
    rawContent: NotRequired[str | None]


class LlmChannelPredictToServerPacketCancel(
    LMStudioStruct["LlmChannelPredictToServerPacketCancelDict"], kw_only=True
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class LlmChannelPredictToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class LlmChannelGenerateWithGeneratorToClientPacketFragment(
    LMStudioStruct["LlmChannelGenerateWithGeneratorToClientPacketFragmentDict"],
    kw_only=True,
    tag_field="type",
    tag="fragment",
):
    type: ClassVar[Annotated[Literal["fragment"], Meta(title="Type")]] = "fragment"
    fragment: LlmPredictionFragment


class LlmChannelGenerateWithGeneratorToClientPacketFragmentDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketFragment.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["fragment"]
    fragment: LlmPredictionFragmentDict


class LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgress(
    LMStudioStruct[
        "LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgressDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="promptProcessingProgress",
):
    type: ClassVar[
        Annotated[Literal["promptProcessingProgress"], Meta(title="Type")]
    ] = "promptProcessingProgress"
    progress: float


class LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgressDict(
    TypedDict
):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["promptProcessingProgress"]
    progress: float


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStart(
    LMStudioStruct[
        "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStartDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationStart",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationStart"], Meta(title="Type")]
    ] = "toolCallGenerationStart"


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStartDict(
    TypedDict
):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStart.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationStart"]


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceived(
    LMStudioStruct[
        "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceivedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationNameReceived",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationNameReceived"], Meta(title="Type")]
    ] = "toolCallGenerationNameReceived"
    name: str


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceivedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceived.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationNameReceived"]
    name: str


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGenerated(
    LMStudioStruct[
        "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGeneratedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationArgumentFragmentGenerated",
):
    type: ClassVar[
        Annotated[
            Literal["toolCallGenerationArgumentFragmentGenerated"], Meta(title="Type")
        ]
    ] = "toolCallGenerationArgumentFragmentGenerated"
    content: str


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGeneratedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGenerated.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationArgumentFragmentGenerated"]
    content: str


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailed(
    LMStudioStruct[
        "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationFailed",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationFailed"], Meta(title="Type")]
    ] = "toolCallGenerationFailed"


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailed.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationFailed"]


class LlmChannelGenerateWithGeneratorToClientPacketSuccess(
    LMStudioStruct["LlmChannelGenerateWithGeneratorToClientPacketSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="success",
):
    type: ClassVar[Annotated[Literal["success"], Meta(title="Type")]] = "success"


class LlmChannelGenerateWithGeneratorToClientPacketSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["success"]


class LlmChannelGenerateWithGeneratorToServerPacketCancel(
    LMStudioStruct["LlmChannelGenerateWithGeneratorToServerPacketCancelDict"],
    kw_only=True,
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class LlmChannelGenerateWithGeneratorToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class PluginsChannelRegisterDevelopmentPluginToClientPacketReady(
    LMStudioStruct["PluginsChannelRegisterDevelopmentPluginToClientPacketReadyDict"],
    kw_only=True,
):
    type: Annotated[Literal["ready"], Meta(title="Type")]
    client_identifier: str = field(name="clientIdentifier")
    client_passkey: str = field(name="clientPasskey")


class PluginsChannelRegisterDevelopmentPluginToClientPacketReadyDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelRegisterDevelopmentPluginToClientPacketReady.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["ready"], Meta(title="Type")]
    clientIdentifier: str
    clientPasskey: str


class PluginsChannelRegisterDevelopmentPluginToServerPacketEnd(
    LMStudioStruct["PluginsChannelRegisterDevelopmentPluginToServerPacketEndDict"],
    kw_only=True,
):
    type: Annotated[Literal["end"], Meta(title="Type")]


class PluginsChannelRegisterDevelopmentPluginToServerPacketEndDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelRegisterDevelopmentPluginToServerPacketEnd.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["end"], Meta(title="Type")]


class PluginsChannelSetPreprocessorToClientPacketAbort(
    LMStudioStruct["PluginsChannelSetPreprocessorToClientPacketAbortDict"],
    kw_only=True,
    tag_field="type",
    tag="abort",
):
    type: ClassVar[Annotated[Literal["abort"], Meta(title="Type")]] = "abort"
    task_id: str = field(name="taskId")


class PluginsChannelSetPreprocessorToClientPacketAbortDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPreprocessorToClientPacketAbort.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["abort"]
    taskId: str


class PluginsChannelSetPreprocessorToServerPacketAborted(
    LMStudioStruct["PluginsChannelSetPreprocessorToServerPacketAbortedDict"],
    kw_only=True,
    tag_field="type",
    tag="aborted",
):
    type: ClassVar[Annotated[Literal["aborted"], Meta(title="Type")]] = "aborted"
    task_id: str = field(name="taskId")


class PluginsChannelSetPreprocessorToServerPacketAbortedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPreprocessorToServerPacketAborted.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["aborted"]
    taskId: str


class PluginsChannelSetPreprocessorToServerPacketError(
    LMStudioStruct["PluginsChannelSetPreprocessorToServerPacketErrorDict"],
    kw_only=True,
    tag_field="type",
    tag="error",
):
    type: ClassVar[Annotated[Literal["error"], Meta(title="Type")]] = "error"
    task_id: str = field(name="taskId")
    error: SerializedLMSExtendedError


class PluginsChannelSetPreprocessorToServerPacketErrorDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPreprocessorToServerPacketError.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["error"]
    taskId: str
    error: SerializedLMSExtendedErrorDict


class PluginsChannelSetPredictionLoopHandlerToClientPacketAbort(
    LMStudioStruct["PluginsChannelSetPredictionLoopHandlerToClientPacketAbortDict"],
    kw_only=True,
    tag_field="type",
    tag="abort",
):
    type: ClassVar[Annotated[Literal["abort"], Meta(title="Type")]] = "abort"
    task_id: str = field(name="taskId")


class PluginsChannelSetPredictionLoopHandlerToClientPacketAbortDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPredictionLoopHandlerToClientPacketAbort.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["abort"]
    taskId: str


class PluginsChannelSetPredictionLoopHandlerToServerPacketComplete(
    LMStudioStruct["PluginsChannelSetPredictionLoopHandlerToServerPacketCompleteDict"],
    kw_only=True,
    tag_field="type",
    tag="complete",
):
    type: ClassVar[Annotated[Literal["complete"], Meta(title="Type")]] = "complete"
    task_id: str = field(name="taskId")


class PluginsChannelSetPredictionLoopHandlerToServerPacketCompleteDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPredictionLoopHandlerToServerPacketComplete.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["complete"]
    taskId: str


class PluginsChannelSetPredictionLoopHandlerToServerPacketAborted(
    LMStudioStruct["PluginsChannelSetPredictionLoopHandlerToServerPacketAbortedDict"],
    kw_only=True,
    tag_field="type",
    tag="aborted",
):
    type: ClassVar[Annotated[Literal["aborted"], Meta(title="Type")]] = "aborted"
    task_id: str = field(name="taskId")


class PluginsChannelSetPredictionLoopHandlerToServerPacketAbortedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPredictionLoopHandlerToServerPacketAborted.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["aborted"]
    taskId: str


class PluginsChannelSetPredictionLoopHandlerToServerPacketError(
    LMStudioStruct["PluginsChannelSetPredictionLoopHandlerToServerPacketErrorDict"],
    kw_only=True,
    tag_field="type",
    tag="error",
):
    type: ClassVar[Annotated[Literal["error"], Meta(title="Type")]] = "error"
    task_id: str = field(name="taskId")
    error: SerializedLMSExtendedError


class PluginsChannelSetPredictionLoopHandlerToServerPacketErrorDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPredictionLoopHandlerToServerPacketError.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["error"]
    taskId: str
    error: SerializedLMSExtendedErrorDict


class PluginsChannelSetToolsProviderToClientPacketDiscardSession(
    LMStudioStruct["PluginsChannelSetToolsProviderToClientPacketDiscardSessionDict"],
    kw_only=True,
    tag_field="type",
    tag="discardSession",
):
    type: ClassVar[Annotated[Literal["discardSession"], Meta(title="Type")]] = (
        "discardSession"
    )
    session_id: str = field(name="sessionId")


class PluginsChannelSetToolsProviderToClientPacketDiscardSessionDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToClientPacketDiscardSession.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["discardSession"]
    sessionId: str


class PluginsChannelSetToolsProviderToClientPacketCallTool(
    LMStudioStruct["PluginsChannelSetToolsProviderToClientPacketCallToolDict"],
    kw_only=True,
    tag_field="type",
    tag="callTool",
):
    type: ClassVar[Annotated[Literal["callTool"], Meta(title="Type")]] = "callTool"
    session_id: str = field(name="sessionId")
    call_id: str = field(name="callId")
    tool_name: str = field(name="toolName")
    parameters: JsonSerializable


class PluginsChannelSetToolsProviderToClientPacketCallToolDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToClientPacketCallTool.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["callTool"]
    sessionId: str
    callId: str
    toolName: str
    parameters: JsonSerializable


class PluginsChannelSetToolsProviderToClientPacketAbortToolCall(
    LMStudioStruct["PluginsChannelSetToolsProviderToClientPacketAbortToolCallDict"],
    kw_only=True,
    tag_field="type",
    tag="abortToolCall",
):
    type: ClassVar[Annotated[Literal["abortToolCall"], Meta(title="Type")]] = (
        "abortToolCall"
    )
    session_id: str = field(name="sessionId")
    call_id: str = field(name="callId")


class PluginsChannelSetToolsProviderToClientPacketAbortToolCallDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToClientPacketAbortToolCall.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["abortToolCall"]
    sessionId: str
    callId: str


class PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailed(
    LMStudioStruct[
        "PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="sessionInitializationFailed",
):
    type: ClassVar[
        Annotated[Literal["sessionInitializationFailed"], Meta(title="Type")]
    ] = "sessionInitializationFailed"
    session_id: str = field(name="sessionId")
    error: SerializedLMSExtendedError


class PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailed.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["sessionInitializationFailed"]
    sessionId: str
    error: SerializedLMSExtendedErrorDict


class PluginsChannelSetToolsProviderToServerPacketToolCallComplete(
    LMStudioStruct["PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallComplete",
):
    type: ClassVar[Annotated[Literal["toolCallComplete"], Meta(title="Type")]] = (
        "toolCallComplete"
    )
    session_id: str = field(name="sessionId")
    call_id: str = field(name="callId")
    result: JsonSerializable


class PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToServerPacketToolCallComplete.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallComplete"]
    sessionId: str
    callId: str
    result: JsonSerializable


class PluginsChannelSetToolsProviderToServerPacketToolCallError(
    LMStudioStruct["PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallError",
):
    type: ClassVar[Annotated[Literal["toolCallError"], Meta(title="Type")]] = (
        "toolCallError"
    )
    session_id: str = field(name="sessionId")
    call_id: str = field(name="callId")
    error: SerializedLMSExtendedError


class PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToServerPacketToolCallError.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallError"]
    sessionId: str
    callId: str
    error: SerializedLMSExtendedErrorDict


class PluginsChannelSetToolsProviderToServerPacketToolCallStatus(
    LMStudioStruct["PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallStatus",
):
    type: ClassVar[Annotated[Literal["toolCallStatus"], Meta(title="Type")]] = (
        "toolCallStatus"
    )
    session_id: str = field(name="sessionId")
    call_id: str = field(name="callId")
    status_text: str = field(name="statusText")


class PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToServerPacketToolCallStatus.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallStatus"]
    sessionId: str
    callId: str
    statusText: str


class PluginsChannelSetToolsProviderToServerPacketToolCallWarn(
    LMStudioStruct["PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallWarn",
):
    type: ClassVar[Annotated[Literal["toolCallWarn"], Meta(title="Type")]] = (
        "toolCallWarn"
    )
    session_id: str = field(name="sessionId")
    call_id: str = field(name="callId")
    warn_text: str = field(name="warnText")


class PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToServerPacketToolCallWarn.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallWarn"]
    sessionId: str
    callId: str
    warnText: str


class PluginsChannelSetGeneratorToClientPacketAbort(
    LMStudioStruct["PluginsChannelSetGeneratorToClientPacketAbortDict"],
    kw_only=True,
    tag_field="type",
    tag="abort",
):
    type: ClassVar[Annotated[Literal["abort"], Meta(title="Type")]] = "abort"
    task_id: str = field(name="taskId")


class PluginsChannelSetGeneratorToClientPacketAbortDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToClientPacketAbort.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["abort"]
    taskId: str


class PluginsChannelSetGeneratorToServerPacketComplete(
    LMStudioStruct["PluginsChannelSetGeneratorToServerPacketCompleteDict"],
    kw_only=True,
    tag_field="type",
    tag="complete",
):
    type: ClassVar[Annotated[Literal["complete"], Meta(title="Type")]] = "complete"
    task_id: str = field(name="taskId")


class PluginsChannelSetGeneratorToServerPacketCompleteDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketComplete.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["complete"]
    taskId: str


class PluginsChannelSetGeneratorToServerPacketAborted(
    LMStudioStruct["PluginsChannelSetGeneratorToServerPacketAbortedDict"],
    kw_only=True,
    tag_field="type",
    tag="aborted",
):
    type: ClassVar[Annotated[Literal["aborted"], Meta(title="Type")]] = "aborted"
    task_id: str = field(name="taskId")


class PluginsChannelSetGeneratorToServerPacketAbortedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketAborted.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["aborted"]
    taskId: str


class PluginsChannelSetGeneratorToServerPacketError(
    LMStudioStruct["PluginsChannelSetGeneratorToServerPacketErrorDict"],
    kw_only=True,
    tag_field="type",
    tag="error",
):
    type: ClassVar[Annotated[Literal["error"], Meta(title="Type")]] = "error"
    task_id: str = field(name="taskId")
    error: SerializedLMSExtendedError


class PluginsChannelSetGeneratorToServerPacketErrorDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketError.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["error"]
    taskId: str
    error: SerializedLMSExtendedErrorDict


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationStarted(
    LMStudioStruct[
        "PluginsChannelSetGeneratorToServerPacketToolCallGenerationStartedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationStarted",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationStarted"], Meta(title="Type")]
    ] = "toolCallGenerationStarted"
    task_id: str = field(name="taskId")


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationStartedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketToolCallGenerationStarted.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationStarted"]
    taskId: str


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceived(
    LMStudioStruct[
        "PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceivedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationNameReceived",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationNameReceived"], Meta(title="Type")]
    ] = "toolCallGenerationNameReceived"
    task_id: str = field(name="taskId")
    tool_name: str = field(name="toolName")


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceivedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceived.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationNameReceived"]
    taskId: str
    toolName: str


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGenerated(
    LMStudioStruct[
        "PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGeneratedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationArgumentFragmentGenerated",
):
    type: ClassVar[
        Annotated[
            Literal["toolCallGenerationArgumentFragmentGenerated"], Meta(title="Type")
        ]
    ] = "toolCallGenerationArgumentFragmentGenerated"
    task_id: str = field(name="taskId")
    content: str


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGeneratedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGenerated.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationArgumentFragmentGenerated"]
    taskId: str
    content: str


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailed(
    LMStudioStruct[
        "PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationFailed",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationFailed"], Meta(title="Type")]
    ] = "toolCallGenerationFailed"
    task_id: str = field(name="taskId")
    error: SerializedLMSExtendedError


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailed.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationFailed"]
    taskId: str
    error: SerializedLMSExtendedErrorDict


class RepositoryChannelDownloadModelToClientPacketDownloadProgress(
    LMStudioStruct["RepositoryChannelDownloadModelToClientPacketDownloadProgressDict"],
    kw_only=True,
    tag_field="type",
    tag="downloadProgress",
):
    type: ClassVar[Annotated[Literal["downloadProgress"], Meta(title="Type")]] = (
        "downloadProgress"
    )
    update: DownloadProgressUpdate


class RepositoryChannelDownloadModelToClientPacketDownloadProgressDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadModelToClientPacketDownloadProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["downloadProgress"]
    update: DownloadProgressUpdateDict


class RepositoryChannelDownloadModelToClientPacketStartFinalizing(
    LMStudioStruct["RepositoryChannelDownloadModelToClientPacketStartFinalizingDict"],
    kw_only=True,
    tag_field="type",
    tag="startFinalizing",
):
    type: ClassVar[Annotated[Literal["startFinalizing"], Meta(title="Type")]] = (
        "startFinalizing"
    )


class RepositoryChannelDownloadModelToClientPacketStartFinalizingDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadModelToClientPacketStartFinalizing.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["startFinalizing"]


class RepositoryChannelDownloadModelToClientPacketSuccess(
    LMStudioStruct["RepositoryChannelDownloadModelToClientPacketSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="success",
):
    type: ClassVar[Annotated[Literal["success"], Meta(title="Type")]] = "success"
    default_identifier: str = field(name="defaultIdentifier")


class RepositoryChannelDownloadModelToClientPacketSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadModelToClientPacketSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["success"]
    defaultIdentifier: str


class RepositoryChannelDownloadModelToServerPacketCancel(
    LMStudioStruct["RepositoryChannelDownloadModelToServerPacketCancelDict"],
    kw_only=True,
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class RepositoryChannelDownloadModelToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadModelToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class RepositoryChannelDownloadArtifactToClientPacketDownloadProgress(
    LMStudioStruct[
        "RepositoryChannelDownloadArtifactToClientPacketDownloadProgressDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="downloadProgress",
):
    type: ClassVar[Annotated[Literal["downloadProgress"], Meta(title="Type")]] = (
        "downloadProgress"
    )
    update: DownloadProgressUpdate


class RepositoryChannelDownloadArtifactToClientPacketDownloadProgressDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadArtifactToClientPacketDownloadProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["downloadProgress"]
    update: DownloadProgressUpdateDict


class RepositoryChannelDownloadArtifactToClientPacketStartFinalizing(
    LMStudioStruct[
        "RepositoryChannelDownloadArtifactToClientPacketStartFinalizingDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="startFinalizing",
):
    type: ClassVar[Annotated[Literal["startFinalizing"], Meta(title="Type")]] = (
        "startFinalizing"
    )


class RepositoryChannelDownloadArtifactToClientPacketStartFinalizingDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadArtifactToClientPacketStartFinalizing.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["startFinalizing"]


class RepositoryChannelDownloadArtifactToClientPacketSuccess(
    LMStudioStruct["RepositoryChannelDownloadArtifactToClientPacketSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="success",
):
    type: ClassVar[Annotated[Literal["success"], Meta(title="Type")]] = "success"


class RepositoryChannelDownloadArtifactToClientPacketSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadArtifactToClientPacketSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["success"]


class RepositoryChannelDownloadArtifactToServerPacketCancel(
    LMStudioStruct["RepositoryChannelDownloadArtifactToServerPacketCancelDict"],
    kw_only=True,
):
    type: Annotated[Literal["cancel"], Meta(title="Type")]


class RepositoryChannelDownloadArtifactToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelDownloadArtifactToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["cancel"], Meta(title="Type")]


class RepositoryChannelPushArtifactToClientPacketMessage(
    LMStudioStruct["RepositoryChannelPushArtifactToClientPacketMessageDict"],
    kw_only=True,
):
    type: Annotated[Literal["message"], Meta(title="Type")]
    message: str


class RepositoryChannelPushArtifactToClientPacketMessageDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelPushArtifactToClientPacketMessage.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["message"], Meta(title="Type")]
    message: str


class RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrl(
    LMStudioStruct[
        "RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrlDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="authenticationUrl",
):
    type: ClassVar[Annotated[Literal["authenticationUrl"], Meta(title="Type")]] = (
        "authenticationUrl"
    )
    url: str


class RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrlDict(
    TypedDict
):
    """Corresponding typed dictionary definition for RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrl.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["authenticationUrl"]
    url: str


class RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticated(
    LMStudioStruct[
        "RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticatedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="authenticated",
):
    type: ClassVar[Annotated[Literal["authenticated"], Meta(title="Type")]] = (
        "authenticated"
    )


class RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticatedDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticated.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["authenticated"]


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgress(
    LMStudioStruct[
        "RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgressDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="downloadProgress",
):
    type: ClassVar[Annotated[Literal["downloadProgress"], Meta(title="Type")]] = (
        "downloadProgress"
    )
    update: DownloadProgressUpdate


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgressDict(
    TypedDict
):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgress.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["downloadProgress"]
    update: DownloadProgressUpdateDict


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizing(
    LMStudioStruct[
        "RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizingDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="startFinalizing",
):
    type: ClassVar[Annotated[Literal["startFinalizing"], Meta(title="Type")]] = (
        "startFinalizing"
    )


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizingDict(
    TypedDict
):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizing.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["startFinalizing"]


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccess(
    LMStudioStruct[
        "RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccessDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="success",
):
    type: ClassVar[Annotated[Literal["success"], Meta(title="Type")]] = "success"


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["success"]


class RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancel(
    LMStudioStruct[
        "RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancelDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="cancel",
):
    type: ClassVar[Annotated[Literal["cancel"], Meta(title="Type")]] = "cancel"


class RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancelDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["cancel"]


class RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommit(
    LMStudioStruct[
        "RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommitDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="commit",
):
    type: ClassVar[Annotated[Literal["commit"], Meta(title="Type")]] = "commit"


class RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommitDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommit.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["commit"]


Name = Annotated[
    str, Meta(max_length=100, min_length=1, pattern="^[a-z0-9]+(?:[-.][a-z0-9]+)*$")
]
Revision = int
Tags = Sequence[str]
Description = str
NoAutoDismiss = bool
Title = str
MaxContextLength = int
Architecture = str
DisplayName = str
ModelKeyModel = str
ParamsString = str
Path = str
SizeBytes = int
ContextLength = int
Identifier = str
InstanceReference = str
Fields = Sequence[KvConfigField]
TrainedForToolUse = bool
Vision = bool
ContextOverflowPolicy = LlmContextOverflowPolicy
CpuThreads = int
DraftModel = str
MaxTokensModel = Any | MaxTokens | bool
MaxTokensModelDict = bool | Any | int
MinPSampling = Any | float | bool
Raw = KvConfig
ReasoningParsing = LlmReasoningParsing
RepeatPenalty = Any | float | bool
SpeculativeDecodingMinContinueDraftingProbability = float
SpeculativeDecodingMinDraftLengthToConsider = Annotated[int, Meta(ge=0)]
SpeculativeDecodingNumDraftTokensExact = Annotated[int, Meta(ge=1)]
StopStrings = Sequence[str]
Temperature = Annotated[float, Meta(ge=0.0)]
ToolCallStopStrings = Sequence[str]
TopKSampling = float
TopPSampling = Any | float | bool
Key = str


class ArtifactArtifactDependency(
    LMStudioStruct["ArtifactArtifactDependencyDict"],
    kw_only=True,
    tag_field="type",
    tag="artifact",
):
    type: ClassVar[Annotated[Literal["artifact"], Meta(title="Type")]] = "artifact"
    purpose: ArtifactDependencyPurpose
    owner: KebabCase
    name: KebabCaseWithDots


class ArtifactArtifactDependencyDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactArtifactDependency.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["artifact"]
    purpose: ArtifactDependencyPurpose
    owner: str
    name: str


class ArtifactDependencyBase(
    LMStudioStruct["ArtifactDependencyBaseDict"], kw_only=True
):
    purpose: ArtifactDependencyPurpose


class ArtifactDependencyBaseDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactDependencyBase.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    purpose: ArtifactDependencyPurpose


class FileHandle(
    LMStudioStruct["FileHandleDict"], kw_only=True, tag_field="type", tag="file"
):
    type: ClassVar[Annotated[Literal["file"], Meta(title="Type")]] = "file"
    name: str
    identifier: str
    size_bytes: int = field(name="sizeBytes")
    file_type: FileType = field(name="fileType")


class FileHandleDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessagePartFileData.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["file"]
    name: str
    identifier: str
    sizeBytes: int
    fileType: FileType


class ToolCallRequest(LMStudioStruct["ToolCallRequestDict"], kw_only=True):
    type: Annotated[Literal["function"], Meta(title="Type")]
    name: str
    id: str | None = None
    arguments: Mapping[str, JsonSerializable] | None = None


class ToolCallRequestDict(TypedDict):
    """Corresponding typed dictionary definition for FunctionToolCallRequest.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["function"], Meta(title="Type")]
    name: str
    id: NotRequired[str | None]
    arguments: NotRequired[Mapping[str, JsonSerializable] | None]


ToolCallRequest = ToolCallRequest
DiagnosticsLogEventData = DiagnosticsLogEventDataLlmPredictionInput


class DiagnosticsLogEvent(LMStudioStruct["DiagnosticsLogEventDict"], kw_only=True):
    timestamp: float
    data: DiagnosticsLogEventData


class DiagnosticsLogEventDict(TypedDict):
    """Corresponding typed dictionary definition for DiagnosticsLogEvent.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    timestamp: float
    data: DiagnosticsLogEventDataLlmPredictionInputDict


class EmbeddingModelInfo(
    LMStudioStruct["EmbeddingModelInfoDict"],
    kw_only=True,
    tag_field="type",
    tag="embedding",
):
    type: ClassVar[Annotated[Literal["embedding"], Meta(title="Type")]] = "embedding"
    model_key: str = field(name="modelKey")
    format: ModelCompatibilityType
    display_name: str = field(name="displayName")
    path: str
    size_bytes: int = field(name="sizeBytes")
    max_context_length: MaxContextLength = field(name="maxContextLength")
    params_string: str | None = field(name="paramsString", default=None)
    architecture: str | None = None


class EmbeddingModelInfoDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingModelInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["embedding"]
    modelKey: str
    format: ModelCompatibilityType
    displayName: str
    path: str
    sizeBytes: int
    maxContextLength: int
    paramsString: NotRequired[str | None]
    architecture: NotRequired[str | None]


class EmbeddingModelInstanceInfo(
    LMStudioStruct["EmbeddingModelInstanceInfoDict"],
    kw_only=True,
    tag_field="type",
    tag="embedding",
):
    type: ClassVar[Annotated[Literal["embedding"], Meta(title="Type")]] = "embedding"
    model_key: ModelKeyModel = field(name="modelKey")
    format: ModelCompatibilityType
    display_name: DisplayName = field(name="displayName")
    path: Path
    size_bytes: SizeBytes = field(name="sizeBytes")
    identifier: str
    instance_reference: str = field(name="instanceReference")
    max_context_length: MaxContextLength = field(name="maxContextLength")
    context_length: ContextLength = field(name="contextLength")
    params_string: ParamsString | None = field(name="paramsString", default=None)
    architecture: Architecture | None = None


class EmbeddingModelInstanceInfoDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingModelInstanceInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["embedding"]
    modelKey: str
    format: ModelCompatibilityType
    displayName: str
    path: str
    sizeBytes: int
    identifier: str
    instanceReference: str
    maxContextLength: int
    contextLength: int
    paramsString: NotRequired[str | None]
    architecture: NotRequired[str | None]


ParsedFileIdentifier = ParsedFileIdentifierLocal | ParsedFileIdentifierBase64
ParsedFileIdentifierDict = (
    ParsedFileIdentifierLocalDict | ParsedFileIdentifierBase64Dict
)


class GpuSplitConfig(LMStudioStruct["GpuSplitConfigDict"], kw_only=True):
    strategy: GpuSplitStrategy
    disabled_gpus: Sequence[DisabledGpu] = field(name="disabledGpus")
    priority: Sequence[PriorityItem]
    custom_ratio: Sequence[CustomRatioItem] = field(name="customRatio")


class GpuSplitConfigDict(TypedDict):
    """Corresponding typed dictionary definition for GpuSplitConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    strategy: GpuSplitStrategy
    disabledGpus: Sequence[int]
    priority: Sequence[int]
    customRatio: Sequence[float]


ContentBlockStyle = (
    ContentBlockStyleDefault | ContentBlockStyleCustomLabel | ContentBlockStyleThinking
)
ContentBlockStyleDict = (
    ContentBlockStyleThinkingDict
    | ContentBlockStyleDefaultDict
    | ContentBlockStyleCustomLabelDict
)
LlmContextReference = LlmContextReferenceJsonFile | LlmContextReferenceYamlFile
LlmContextReferenceDict = (
    LlmContextReferenceJsonFileDict | LlmContextReferenceYamlFileDict
)


class GpuSetting(LMStudioStruct["GpuSettingDict"], kw_only=True):
    ratio: LlmLlamaAccelerationOffloadRatio | None = None
    main_gpu: int | None = field(name="mainGpu", default=None)
    split_strategy: LlmSplitStrategy | None = field(name="splitStrategy", default=None)
    disabled_gpus: Sequence[int] | None = field(name="disabledGpus", default=None)


class GpuSettingDict(TypedDict):
    """Corresponding typed dictionary definition for GpuSetting.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    ratio: NotRequired[LlmLlamaAccelerationOffloadRatioDict | None]
    mainGpu: NotRequired[int | None]
    splitStrategy: NotRequired[LlmSplitStrategy | None]
    disabledGpus: NotRequired[Sequence[int] | None]


class LlmLoadModelConfig(LMStudioStruct["LlmLoadModelConfigDict"], kw_only=True):
    gpu: GpuSetting | None = None
    gpu_strict_vram_cap: bool | None = field(name="gpuStrictVramCap", default=None)
    offload_kv_cache_to_gpu: bool | None = field(
        name="offloadKVCacheToGpu", default=None
    )
    context_length: Annotated[int, Meta(ge=1)] | None = field(
        name="contextLength", default=None
    )
    rope_frequency_base: float | None = field(name="ropeFrequencyBase", default=None)
    rope_frequency_scale: float | None = field(name="ropeFrequencyScale", default=None)
    eval_batch_size: Annotated[int, Meta(ge=1)] | None = field(
        name="evalBatchSize", default=None
    )
    flash_attention: bool | None = field(name="flashAttention", default=None)
    keep_model_in_memory: bool | None = field(name="keepModelInMemory", default=None)
    seed: int | None = None
    use_fp16_for_kv_cache: bool | None = field(name="useFp16ForKVCache", default=None)
    try_mmap: bool | None = field(name="tryMmap", default=None)
    num_experts: int | None = field(name="numExperts", default=None)
    llama_k_cache_quantization_type: (
        Literal["f32", "f16", "q8_0", "q4_0", "q4_1", "iq4_nl", "q5_0", "q5_1"]
        | bool
        | None
    ) = field(name="llamaKCacheQuantizationType", default=None)
    llama_v_cache_quantization_type: (
        Literal["f32", "f16", "q8_0", "q4_0", "q4_1", "iq4_nl", "q5_0", "q5_1"]
        | bool
        | None
    ) = field(name="llamaVCacheQuantizationType", default=None)


class LlmLoadModelConfigDict(TypedDict):
    """Corresponding typed dictionary definition for LlmLoadModelConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    gpu: NotRequired[GpuSettingDict | None]
    gpuStrictVramCap: NotRequired[bool | None]
    offloadKVCacheToGpu: NotRequired[bool | None]
    contextLength: NotRequired[Annotated[int, Meta(ge=1)] | None]
    ropeFrequencyBase: NotRequired[float | None]
    ropeFrequencyScale: NotRequired[float | None]
    evalBatchSize: NotRequired[Annotated[int, Meta(ge=1)] | None]
    flashAttention: NotRequired[bool | None]
    keepModelInMemory: NotRequired[bool | None]
    seed: NotRequired[int | None]
    useFp16ForKVCache: NotRequired[bool | None]
    tryMmap: NotRequired[bool | None]
    numExperts: NotRequired[int | None]
    llamaKCacheQuantizationType: NotRequired[
        Literal["f32", "f16", "q8_0", "q4_0", "q4_1", "iq4_nl", "q5_0", "q5_1"]
        | bool
        | None
    ]
    llamaVCacheQuantizationType: NotRequired[
        Literal["f32", "f16", "q8_0", "q4_0", "q4_1", "iq4_nl", "q5_0", "q5_1"]
        | bool
        | None
    ]


class LlmInfo(LMStudioStruct["LlmInfoDict"], kw_only=True, tag_field="type", tag="llm"):
    type: ClassVar[Annotated[Literal["llm"], Meta(title="Type")]] = "llm"
    model_key: ModelKeyModel = field(name="modelKey")
    format: ModelCompatibilityType
    display_name: DisplayName = field(name="displayName")
    path: Path
    size_bytes: SizeBytes = field(name="sizeBytes")
    vision: Vision
    trained_for_tool_use: TrainedForToolUse = field(name="trainedForToolUse")
    max_context_length: MaxContextLength = field(name="maxContextLength")
    params_string: ParamsString | None = field(name="paramsString", default=None)
    architecture: Architecture | None = None


class LlmInfoDict(TypedDict):
    """Corresponding typed dictionary definition for LlmInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["llm"]
    modelKey: str
    format: ModelCompatibilityType
    displayName: str
    path: str
    sizeBytes: int
    vision: bool
    trainedForToolUse: bool
    maxContextLength: int
    paramsString: NotRequired[str | None]
    architecture: NotRequired[str | None]


class LlmInstanceInfo(
    LMStudioStruct["LlmInstanceInfoDict"], kw_only=True, tag_field="type", tag="llm"
):
    type: ClassVar[Annotated[Literal["llm"], Meta(title="Type")]] = "llm"
    model_key: ModelKeyModel = field(name="modelKey")
    format: ModelCompatibilityType
    display_name: DisplayName = field(name="displayName")
    path: Path
    size_bytes: SizeBytes = field(name="sizeBytes")
    identifier: Identifier
    instance_reference: InstanceReference = field(name="instanceReference")
    vision: Vision
    trained_for_tool_use: TrainedForToolUse = field(name="trainedForToolUse")
    max_context_length: MaxContextLength = field(name="maxContextLength")
    context_length: ContextLength = field(name="contextLength")
    params_string: ParamsString | None = field(name="paramsString", default=None)
    architecture: Architecture | None = None


class LlmInstanceInfoDict(TypedDict):
    """Corresponding typed dictionary definition for LlmInstanceInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["llm"]
    modelKey: str
    format: ModelCompatibilityType
    displayName: str
    path: str
    sizeBytes: int
    identifier: str
    instanceReference: str
    vision: bool
    trainedForToolUse: bool
    maxContextLength: int
    contextLength: int
    paramsString: NotRequired[str | None]
    architecture: NotRequired[str | None]


LlmLlamaLogitBiasConfigItem = Sequence[float | LlmLlamaSingleLogitBiasModification]
LlmLlamaLogitBiasConfig = Sequence[LlmLlamaLogitBiasConfigItem]


class LlmPredictionFragmentInputOpts(
    LMStudioStruct["LlmPredictionFragmentInputOptsDict"], kw_only=True
):
    token_count: int | None = field(name="tokenCount", default=None)
    contains_drafted: bool | None = field(name="containsDrafted", default=None)
    reasoning_type: LlmPredictionFragmentReasoningType | None = field(
        name="reasoningType", default=None
    )


class LlmPredictionFragmentInputOptsDict(TypedDict):
    """Corresponding typed dictionary definition for LlmPredictionFragmentInputOpts.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    tokenCount: NotRequired[int | None]
    containsDrafted: NotRequired[bool | None]
    reasoningType: NotRequired[LlmPredictionFragmentReasoningType | None]


class LlmPredictionStats(LMStudioStruct["LlmPredictionStatsDict"], kw_only=True):
    stop_reason: LlmPredictionStopReason = field(name="stopReason")
    tokens_per_second: float | None = field(name="tokensPerSecond", default=None)
    num_gpu_layers: float | None = field(name="numGpuLayers", default=None)
    time_to_first_token_sec: float | None = field(
        name="timeToFirstTokenSec", default=None
    )
    prompt_tokens_count: int | None = field(name="promptTokensCount", default=None)
    predicted_tokens_count: int | None = field(
        name="predictedTokensCount", default=None
    )
    total_tokens_count: int | None = field(name="totalTokensCount", default=None)
    used_draft_model_key: str | None = field(name="usedDraftModelKey", default=None)
    total_draft_tokens_count: int | None = field(
        name="totalDraftTokensCount", default=None
    )
    accepted_draft_tokens_count: int | None = field(
        name="acceptedDraftTokensCount", default=None
    )
    rejected_draft_tokens_count: int | None = field(
        name="rejectedDraftTokensCount", default=None
    )
    ignored_draft_tokens_count: int | None = field(
        name="ignoredDraftTokensCount", default=None
    )


class LlmPredictionStatsDict(TypedDict):
    """Corresponding typed dictionary definition for LlmPredictionStats.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    stopReason: LlmPredictionStopReason
    tokensPerSecond: NotRequired[float | None]
    numGpuLayers: NotRequired[float | None]
    timeToFirstTokenSec: NotRequired[float | None]
    promptTokensCount: NotRequired[int | None]
    predictedTokensCount: NotRequired[int | None]
    totalTokensCount: NotRequired[int | None]
    usedDraftModelKey: NotRequired[str | None]
    totalDraftTokensCount: NotRequired[int | None]
    acceptedDraftTokensCount: NotRequired[int | None]
    rejectedDraftTokensCount: NotRequired[int | None]
    ignoredDraftTokensCount: NotRequired[int | None]


class LlmPromptTemplate(LMStudioStruct["LlmPromptTemplateDict"], kw_only=True):
    type: LlmPromptTemplateType
    stop_strings: Sequence[str] = field(name="stopStrings")
    manual_prompt_template: LlmManualPromptTemplate | None = field(
        name="manualPromptTemplate", default=None
    )
    jinja_prompt_template: LlmJinjaPromptTemplate | None = field(
        name="jinjaPromptTemplate", default=None
    )


class LlmPromptTemplateDict(TypedDict):
    """Corresponding typed dictionary definition for LlmPromptTemplate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: LlmPromptTemplateType
    stopStrings: Sequence[str]
    manualPromptTemplate: NotRequired[LlmManualPromptTemplateDict | None]
    jinjaPromptTemplate: NotRequired[LlmJinjaPromptTemplateDict | None]


class LlmStructuredPredictionSetting(
    LMStudioStruct["LlmStructuredPredictionSettingDict"], kw_only=True
):
    type: LlmStructuredPredictionType
    json_schema: JsonSerializable | None = field(name="jsonSchema", default=None)
    gbnf_grammar: str | None = field(name="gbnfGrammar", default=None)


class LlmStructuredPredictionSettingDict(TypedDict):
    """Corresponding typed dictionary definition for LlmStructuredPredictionSetting.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: LlmStructuredPredictionType
    jsonSchema: NotRequired[JsonSerializable | None]
    gbnfGrammar: NotRequired[str | None]


LlmToolParameters = LlmToolParametersObject
ProcessingRequest = ProcessingRequestConfirmToolCall | ProcessingRequestTextInput
ProcessingRequestDict = (
    ProcessingRequestConfirmToolCallDict | ProcessingRequestTextInputDict
)
BlockLocation = BlockLocationBeforeId | BlockLocationAfterId
BlockLocationDict = BlockLocationBeforeIdDict | BlockLocationAfterIdDict


class ProcessingUpdateContentBlockCreate(
    LMStudioStruct["ProcessingUpdateContentBlockCreateDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.create",
):
    type: ClassVar[Annotated[Literal["contentBlock.create"], Meta(title="Type")]] = (
        "contentBlock.create"
    )
    id: str
    include_in_context: bool = field(name="includeInContext")
    role_override: Literal["user", "assistant", "system", "tool"] | None = field(
        name="roleOverride", default=None
    )
    style: ContentBlockStyle | None = None
    prefix: str | None = None
    suffix: str | None = None


class ProcessingUpdateContentBlockCreateDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockCreate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.create"]
    id: str
    includeInContext: bool
    roleOverride: NotRequired[Literal["user", "assistant", "system", "tool"] | None]
    style: NotRequired[ContentBlockStyleDict | None]
    prefix: NotRequired[str | None]
    suffix: NotRequired[str | None]


class ProcessingUpdateContentBlockSetStyle(
    LMStudioStruct["ProcessingUpdateContentBlockSetStyleDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.setStyle",
):
    type: ClassVar[Annotated[Literal["contentBlock.setStyle"], Meta(title="Type")]] = (
        "contentBlock.setStyle"
    )
    id: str
    style: ContentBlockStyle


class ProcessingUpdateContentBlockSetStyleDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockSetStyle.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.setStyle"]
    id: str
    style: ContentBlockStyleDict


class StatusStepState(LMStudioStruct["StatusStepStateDict"], kw_only=True):
    status: StatusStepStatus
    text: str


class StatusStepStateDict(TypedDict):
    """Corresponding typed dictionary definition for StatusStepState.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    status: StatusStepStatus
    text: str


ToolStatusStepStateStatus = (
    ToolStatusStepStateStatusGeneratingToolCall
    | ToolStatusStepStateStatusToolCallGenerationFailed
    | ToolStatusStepStateStatusToolCallQueued
    | ToolStatusStepStateStatusConfirmingToolCall
    | ToolStatusStepStateStatusToolCallDenied
    | ToolStatusStepStateStatusCallingTool
    | ToolStatusStepStateStatusToolCallFailed
    | ToolStatusStepStateStatusToolCallSucceeded
)
ToolStatusStepStateStatusDict = (
    ToolStatusStepStateStatusToolCallSucceededDict
    | ToolStatusStepStateStatusToolCallFailedDict
    | ToolStatusStepStateStatusCallingToolDict
    | ToolStatusStepStateStatusToolCallDeniedDict
    | ToolStatusStepStateStatusConfirmingToolCallDict
    | ToolStatusStepStateStatusToolCallQueuedDict
    | ToolStatusStepStateStatusGeneratingToolCallDict
    | ToolStatusStepStateStatusToolCallGenerationFailedDict
)


class HuggingFaceModelDownloadSource(
    LMStudioStruct["HuggingFaceModelDownloadSourceDict"], kw_only=True
):
    type: Annotated[Literal["huggingface"], Meta(title="Type")]
    user: FileName
    repo: FileName


class HuggingFaceModelDownloadSourceDict(TypedDict):
    """Corresponding typed dictionary definition for HuggingFaceModelDownloadSource.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["huggingface"], Meta(title="Type")]
    user: str
    repo: str


ModelDownloadSource = HuggingFaceModelDownloadSource
ModelInfo = LlmInfo | EmbeddingModelInfo
ModelInfoDict = LlmInfoDict | EmbeddingModelInfoDict
ModelInstanceInfo = LlmInstanceInfo | EmbeddingModelInstanceInfo
ModelInstanceInfoDict = LlmInstanceInfoDict | EmbeddingModelInstanceInfoDict


class ModelInfoBase(LMStudioStruct["ModelInfoBaseDict"], kw_only=True):
    model_key: ModelKeyModel = field(name="modelKey")
    format: ModelCompatibilityType
    display_name: DisplayName = field(name="displayName")
    path: Path
    size_bytes: SizeBytes = field(name="sizeBytes")
    params_string: ParamsString | None = field(name="paramsString", default=None)
    architecture: Architecture | None = None


class ModelInfoBaseDict(TypedDict):
    """Corresponding typed dictionary definition for ModelInfoBase.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelKey: str
    format: ModelCompatibilityType
    displayName: str
    path: str
    sizeBytes: int
    paramsString: NotRequired[str | None]
    architecture: NotRequired[str | None]


class ModelInstanceInfoBase(LMStudioStruct["ModelInstanceInfoBaseDict"], kw_only=True):
    model_key: ModelKeyModel = field(name="modelKey")
    format: ModelCompatibilityType
    display_name: DisplayName = field(name="displayName")
    path: Path
    size_bytes: SizeBytes = field(name="sizeBytes")
    identifier: Identifier
    instance_reference: InstanceReference = field(name="instanceReference")
    params_string: ParamsString | None = field(name="paramsString", default=None)
    architecture: Architecture | None = None


class ModelInstanceInfoBaseDict(TypedDict):
    """Corresponding typed dictionary definition for ModelInstanceInfoBase.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelKey: str
    format: ModelCompatibilityType
    displayName: str
    path: str
    sizeBytes: int
    identifier: str
    instanceReference: str
    paramsString: NotRequired[str | None]
    architecture: NotRequired[str | None]


class ModelQuery(LMStudioStruct["ModelQueryDict"], kw_only=True):
    domain: ModelDomainType | None = None
    identifier: ReasonableKeyString | None = None
    path: ReasonableKeyString | None = None
    vision: bool | None = None


class ModelQueryDict(TypedDict):
    """Corresponding typed dictionary definition for ModelQuery.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    domain: NotRequired[ModelDomainType | None]
    identifier: NotRequired[str | None]
    path: NotRequired[str | None]
    vision: NotRequired[bool | None]


ArtifactDownloadPlanNode = (
    ArtifactDownloadPlanNodeArtifact | ArtifactDownloadPlanNodeModel
)
ArtifactDownloadPlanNodeDict = (
    ArtifactDownloadPlanNodeArtifactDict | ArtifactDownloadPlanNodeModelDict
)


class ArtifactDownloadPlan(LMStudioStruct["ArtifactDownloadPlanDict"], kw_only=True):
    nodes: Sequence[ArtifactDownloadPlanNode]
    download_size_bytes: int = field(name="downloadSizeBytes")


class ArtifactDownloadPlanDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactDownloadPlan.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    nodes: Sequence[ArtifactDownloadPlanNodeDict]
    downloadSizeBytes: int


ModelSearchResultIdentifier = (
    ModelSearchResultIdentifierCatalog | ModelSearchResultIdentifierHf
)
ModelSearchResultIdentifierDict = (
    ModelSearchResultIdentifierCatalogDict | ModelSearchResultIdentifierHfDict
)
RetrievalChunkingMethod = RetrievalChunkingMethodRecursiveV1


class Accelerator(LMStudioStruct["AcceleratorDict"], kw_only=True):
    name: str
    device_id: int = field(name="deviceId")
    total_memory_bytes: int = field(name="totalMemoryBytes")
    type: AcceleratorType


class AcceleratorDict(TypedDict):
    """Corresponding typed dictionary definition for Accelerator.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    name: str
    deviceId: int
    totalMemoryBytes: int
    type: AcceleratorType


class Runtime(LMStudioStruct["RuntimeDict"], kw_only=True):
    key: str
    name: str
    accelerators: Sequence[Accelerator]


class RuntimeDict(TypedDict):
    """Corresponding typed dictionary definition for Runtime.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    key: str
    name: str
    accelerators: Sequence[AcceleratorDict]


class VirtualModelBooleanCustomFieldDefinition(
    LMStudioStruct["VirtualModelBooleanCustomFieldDefinitionDict"],
    kw_only=True,
    tag_field="type",
    tag="boolean",
):
    key: str
    display_name: str = field(name="displayName")
    description: str
    type: ClassVar[Annotated[Literal["boolean"], Meta(title="Type")]] = "boolean"
    default_value: bool = field(name="defaultValue")
    effects: Sequence[VirtualModelBooleanCustomFieldDefinitionEffectsItem]


class VirtualModelBooleanCustomFieldDefinitionDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelBooleanCustomFieldDefinition.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    key: str
    displayName: str
    description: str
    type: Literal["boolean"]
    defaultValue: bool
    effects: Sequence[VirtualModelBooleanCustomFieldDefinitionEffectsItemDict]


class VirtualModelCustomFieldDefinitionBase(
    LMStudioStruct["VirtualModelCustomFieldDefinitionBaseDict"], kw_only=True
):
    key: Key
    display_name: DisplayName = field(name="displayName")
    description: Description


class VirtualModelCustomFieldDefinitionBaseDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelCustomFieldDefinitionBase.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    key: str
    displayName: str
    description: str


class VirtualModelDefinitionConcreteModelBase(
    LMStudioStruct["VirtualModelDefinitionConcreteModelBaseDict"], kw_only=True
):
    key: str
    sources: Sequence[ModelDownloadSource]


class VirtualModelDefinitionConcreteModelBaseDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelDefinitionConcreteModelBase.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    key: str
    sources: Sequence[HuggingFaceModelDownloadSourceDict]


class VirtualModelStringCustomFieldDefinition(
    LMStudioStruct["VirtualModelStringCustomFieldDefinitionDict"],
    kw_only=True,
    tag_field="type",
    tag="string",
):
    key: Key
    display_name: DisplayName = field(name="displayName")
    description: Description
    type: ClassVar[Annotated[Literal["string"], Meta(title="Type")]] = "string"
    default_value: str = field(name="defaultValue")
    effects: Sequence[VirtualModelStringCustomFieldDefinitionEffectsItem]


class VirtualModelStringCustomFieldDefinitionDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelStringCustomFieldDefinition.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    key: str
    displayName: str
    description: str
    type: Literal["string"]
    defaultValue: str
    effects: Sequence[VirtualModelCustomFieldSetJinjaVariableEffectDict]


DiagnosticsChannelStreamLogsToServerPacket = (
    DiagnosticsChannelStreamLogsToServerPacketStop
)
EmbeddingRpcListLoadedReturns = Sequence[EmbeddingModelInstanceInfo]


class PseudoEmbeddingRpcListLoaded(
    LMStudioStruct["PseudoEmbeddingRpcListLoadedDict"], kw_only=True
):
    returns: EmbeddingRpcListLoadedReturns
    parameter: EmbeddingRpcListLoadedParameter | None = None


class PseudoEmbeddingRpcListLoadedDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingRpcListLoaded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    returns: EmbeddingRpcListLoadedReturns
    parameter: NotRequired[EmbeddingRpcListLoadedParameter | None]


class EmbeddingRpcGetLoadConfigReturns(
    LMStudioStruct["EmbeddingRpcGetLoadConfigReturnsDict"], kw_only=True
):
    fields: Fields


class EmbeddingRpcGetLoadConfigReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcGetLoadConfigReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fields: Fields


EmbeddingChannelLoadModelToServerPacket = EmbeddingChannelLoadModelToServerPacketCancel
EmbeddingChannelGetOrLoadToServerPacket = EmbeddingChannelGetOrLoadToServerPacketCancel


class FilesChannelRetrieveCreationParameter(
    LMStudioStruct["FilesChannelRetrieveCreationParameterDict"], kw_only=True
):
    query: str
    file_identifiers: Sequence[str] = field(name="fileIdentifiers")
    config: EmbeddingRpcGetLoadConfigReturns


class FilesChannelRetrieveCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for FilesChannelRetrieveCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    query: str
    fileIdentifiers: Sequence[str]
    config: EmbeddingRpcGetLoadConfigReturnsDict


FilesChannelRetrieveToClientPacket = (
    FilesChannelRetrieveToClientPacketOnFileProcessList
    | FilesChannelRetrieveToClientPacketOnFileProcessingStart
    | FilesChannelRetrieveToClientPacketOnFileProcessingEnd
    | FilesChannelRetrieveToClientPacketOnFileProcessingStepStart
    | FilesChannelRetrieveToClientPacketOnFileProcessingStepProgress
    | FilesChannelRetrieveToClientPacketOnFileProcessingStepEnd
    | FilesChannelRetrieveToClientPacketOnSearchingStart
    | FilesChannelRetrieveToClientPacketOnSearchingEnd
    | FilesChannelRetrieveToClientPacketResult
)
FilesChannelRetrieveToClientPacketDict = (
    FilesChannelRetrieveToClientPacketResultDict
    | FilesChannelRetrieveToClientPacketOnSearchingEndDict
    | FilesChannelRetrieveToClientPacketOnSearchingStartDict
    | FilesChannelRetrieveToClientPacketOnFileProcessingStepEndDict
    | FilesChannelRetrieveToClientPacketOnFileProcessingStepProgressDict
    | FilesChannelRetrieveToClientPacketOnFileProcessingStepStartDict
    | FilesChannelRetrieveToClientPacketOnFileProcessingEndDict
    | FilesChannelRetrieveToClientPacketOnFileProcessListDict
    | FilesChannelRetrieveToClientPacketOnFileProcessingStartDict
)
FilesChannelRetrieveToServerPacket = FilesChannelRetrieveToServerPacketStop


class PseudoFilesChannelRetrieve(
    LMStudioStruct["PseudoFilesChannelRetrieveDict"], kw_only=True
):
    creation_parameter: FilesChannelRetrieveCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: FilesChannelRetrieveToClientPacket = field(name="toClientPacket")
    to_server_packet: FilesChannelRetrieveToServerPacket = field(name="toServerPacket")


class PseudoFilesChannelRetrieveDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoFilesChannelRetrieve.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: FilesChannelRetrieveCreationParameterDict
    toClientPacket: FilesChannelRetrieveToClientPacketDict
    toServerPacket: FilesChannelRetrieveToServerPacketStopDict


FilesChannelParseDocumentToClientPacket = (
    FilesChannelParseDocumentToClientPacketParserLoaded
    | FilesChannelParseDocumentToClientPacketProgress
    | FilesChannelParseDocumentToClientPacketResult
)
FilesChannelParseDocumentToClientPacketDict = (
    FilesChannelParseDocumentToClientPacketResultDict
    | FilesChannelParseDocumentToClientPacketParserLoadedDict
    | FilesChannelParseDocumentToClientPacketProgressDict
)
FilesChannelParseDocumentToServerPacket = FilesChannelParseDocumentToServerPacketCancel


class PseudoFilesChannelParseDocument(
    LMStudioStruct["PseudoFilesChannelParseDocumentDict"], kw_only=True
):
    creation_parameter: FilesChannelParseDocumentCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: FilesChannelParseDocumentToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: FilesChannelParseDocumentToServerPacket = field(
        name="toServerPacket"
    )


class PseudoFilesChannelParseDocumentDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoFilesChannelParseDocument.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: FilesChannelParseDocumentCreationParameterDict
    toClientPacket: FilesChannelParseDocumentToClientPacketDict
    toServerPacket: FilesChannelParseDocumentToServerPacketCancelDict


class PseudoFiles(LMStudioStruct["PseudoFilesDict"], kw_only=True):
    rpc_get_local_file_absolute_path: PseudoFilesRpcGetLocalFileAbsolutePath = field(
        name="rpcGetLocalFileAbsolutePath"
    )
    rpc_upload_file_base64: PseudoFilesRpcUploadFileBase64 = field(
        name="rpcUploadFileBase64"
    )
    rpc_get_document_parsing_library: PseudoFilesRpcGetDocumentParsingLibrary = field(
        name="rpcGetDocumentParsingLibrary"
    )
    channel_retrieve: PseudoFilesChannelRetrieve = field(name="channelRetrieve")
    channel_parse_document: PseudoFilesChannelParseDocument = field(
        name="channelParseDocument"
    )


class PseudoFilesDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoFiles.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    rpcGetLocalFileAbsolutePath: PseudoFilesRpcGetLocalFileAbsolutePathDict
    rpcUploadFileBase64: PseudoFilesRpcUploadFileBase64Dict
    rpcGetDocumentParsingLibrary: PseudoFilesRpcGetDocumentParsingLibraryDict
    channelRetrieve: PseudoFilesChannelRetrieveDict
    channelParseDocument: PseudoFilesChannelParseDocumentDict


LlmRpcListLoadedReturns = Sequence[LlmInstanceInfo]


class PseudoLlmRpcListLoaded(
    LMStudioStruct["PseudoLlmRpcListLoadedDict"], kw_only=True
):
    returns: LlmRpcListLoadedReturns
    parameter: LlmRpcListLoadedParameter | None = None


class PseudoLlmRpcListLoadedDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcListLoaded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    returns: LlmRpcListLoadedReturns
    parameter: NotRequired[LlmRpcListLoadedParameter | None]


class LlmRpcGetLoadConfigReturns(
    LMStudioStruct["LlmRpcGetLoadConfigReturnsDict"], kw_only=True
):
    fields: Fields


class LlmRpcGetLoadConfigReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcGetLoadConfigReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    fields: Fields


LlmChannelLoadModelToServerPacket = LlmChannelLoadModelToServerPacketCancel
LlmChannelGetOrLoadToServerPacket = LlmChannelGetOrLoadToServerPacketCancel
LlmChannelPredictToServerPacket = LlmChannelPredictToServerPacketCancel
LlmChannelGenerateWithGeneratorToServerPacket = (
    LlmChannelGenerateWithGeneratorToServerPacketCancel
)


class PluginsRpcProcessingHandleRequestParameter(
    LMStudioStruct["PluginsRpcProcessingHandleRequestParameterDict"], kw_only=True
):
    pci: str
    token: str
    request: ProcessingRequest


class PluginsRpcProcessingHandleRequestParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingHandleRequestParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str
    request: ProcessingRequestDict


PluginsChannelRegisterDevelopmentPluginToClientPacket = (
    PluginsChannelRegisterDevelopmentPluginToClientPacketReady
)
PluginsChannelRegisterDevelopmentPluginToServerPacket = (
    PluginsChannelRegisterDevelopmentPluginToServerPacketEnd
)
PluginsChannelSetPredictionLoopHandlerToServerPacket = (
    PluginsChannelSetPredictionLoopHandlerToServerPacketComplete
    | PluginsChannelSetPredictionLoopHandlerToServerPacketAborted
    | PluginsChannelSetPredictionLoopHandlerToServerPacketError
)
PluginsChannelSetPredictionLoopHandlerToServerPacketDict = (
    PluginsChannelSetPredictionLoopHandlerToServerPacketErrorDict
    | PluginsChannelSetPredictionLoopHandlerToServerPacketCompleteDict
    | PluginsChannelSetPredictionLoopHandlerToServerPacketAbortedDict
)


class RepositoryRpcGetModelDownloadOptionsParameter(
    LMStudioStruct["RepositoryRpcGetModelDownloadOptionsParameterDict"], kw_only=True
):
    model_search_result_identifier: ModelSearchResultIdentifier = field(
        name="modelSearchResultIdentifier"
    )


class RepositoryRpcGetModelDownloadOptionsParameterDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcGetModelDownloadOptionsParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelSearchResultIdentifier: ModelSearchResultIdentifierDict


class PseudoRepositoryRpcGetModelDownloadOptions(
    LMStudioStruct["PseudoRepositoryRpcGetModelDownloadOptionsDict"], kw_only=True
):
    parameter: RepositoryRpcGetModelDownloadOptionsParameter
    returns: RepositoryRpcGetModelDownloadOptionsReturns


class PseudoRepositoryRpcGetModelDownloadOptionsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryRpcGetModelDownloadOptions.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: RepositoryRpcGetModelDownloadOptionsParameterDict
    returns: RepositoryRpcGetModelDownloadOptionsReturnsDict


RepositoryChannelDownloadModelToClientPacket = (
    RepositoryChannelDownloadModelToClientPacketDownloadProgress
    | RepositoryChannelDownloadModelToClientPacketStartFinalizing
    | RepositoryChannelDownloadModelToClientPacketSuccess
)
RepositoryChannelDownloadModelToClientPacketDict = (
    RepositoryChannelDownloadModelToClientPacketSuccessDict
    | RepositoryChannelDownloadModelToClientPacketDownloadProgressDict
    | RepositoryChannelDownloadModelToClientPacketStartFinalizingDict
)
RepositoryChannelDownloadModelToServerPacket = (
    RepositoryChannelDownloadModelToServerPacketCancel
)


class PseudoRepositoryChannelDownloadModel(
    LMStudioStruct["PseudoRepositoryChannelDownloadModelDict"], kw_only=True
):
    creation_parameter: DownloadModelChannelRequest = field(name="creationParameter")
    to_client_packet: RepositoryChannelDownloadModelToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: RepositoryChannelDownloadModelToServerPacket = field(
        name="toServerPacket"
    )


class PseudoRepositoryChannelDownloadModelDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryChannelDownloadModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: DownloadModelChannelRequestDict
    toClientPacket: RepositoryChannelDownloadModelToClientPacketDict
    toServerPacket: RepositoryChannelDownloadModelToServerPacketCancelDict


RepositoryChannelDownloadArtifactToClientPacket = (
    RepositoryChannelDownloadArtifactToClientPacketDownloadProgress
    | RepositoryChannelDownloadArtifactToClientPacketStartFinalizing
    | RepositoryChannelDownloadArtifactToClientPacketSuccess
)
RepositoryChannelDownloadArtifactToClientPacketDict = (
    RepositoryChannelDownloadArtifactToClientPacketSuccessDict
    | RepositoryChannelDownloadArtifactToClientPacketDownloadProgressDict
    | RepositoryChannelDownloadArtifactToClientPacketStartFinalizingDict
)
RepositoryChannelDownloadArtifactToServerPacket = (
    RepositoryChannelDownloadArtifactToServerPacketCancel
)


class PseudoRepositoryChannelDownloadArtifact(
    LMStudioStruct["PseudoRepositoryChannelDownloadArtifactDict"], kw_only=True
):
    creation_parameter: RepositoryChannelDownloadArtifactCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: RepositoryChannelDownloadArtifactToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: RepositoryChannelDownloadArtifactToServerPacket = field(
        name="toServerPacket"
    )


class PseudoRepositoryChannelDownloadArtifactDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryChannelDownloadArtifact.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: RepositoryChannelDownloadArtifactCreationParameterDict
    toClientPacket: RepositoryChannelDownloadArtifactToClientPacketDict
    toServerPacket: RepositoryChannelDownloadArtifactToServerPacketCancelDict


RepositoryChannelPushArtifactToClientPacket = (
    RepositoryChannelPushArtifactToClientPacketMessage
)


class PseudoRepositoryChannelPushArtifact(
    LMStudioStruct["PseudoRepositoryChannelPushArtifactDict"], kw_only=True
):
    creation_parameter: RepositoryChannelPushArtifactCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: RepositoryChannelPushArtifactToClientPacket = field(
        name="toClientPacket"
    )


class PseudoRepositoryChannelPushArtifactDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryChannelPushArtifact.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: RepositoryChannelPushArtifactCreationParameterDict
    toClientPacket: RepositoryChannelPushArtifactToClientPacketMessageDict


RepositoryChannelEnsureAuthenticatedToClientPacket = (
    RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrl
    | RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticated
)
RepositoryChannelEnsureAuthenticatedToClientPacketDict = (
    RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticationUrlDict
    | RepositoryChannelEnsureAuthenticatedToClientPacketAuthenticatedDict
)


class PseudoRepositoryChannelEnsureAuthenticated(
    LMStudioStruct["PseudoRepositoryChannelEnsureAuthenticatedDict"], kw_only=True
):
    to_client_packet: RepositoryChannelEnsureAuthenticatedToClientPacket = field(
        name="toClientPacket"
    )


class PseudoRepositoryChannelEnsureAuthenticatedDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryChannelEnsureAuthenticated.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    toClientPacket: RepositoryChannelEnsureAuthenticatedToClientPacketDict


RepositoryChannelCreateArtifactDownloadPlanToServerPacket = (
    RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancel
    | RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommit
)
RepositoryChannelCreateArtifactDownloadPlanToServerPacketDict = (
    RepositoryChannelCreateArtifactDownloadPlanToServerPacketCancelDict
    | RepositoryChannelCreateArtifactDownloadPlanToServerPacketCommitDict
)
SystemRpcListDownloadedModelsReturns = Sequence[ModelInfo]


class PseudoSystemRpcListDownloadedModels(
    LMStudioStruct["PseudoSystemRpcListDownloadedModelsDict"], kw_only=True
):
    returns: SystemRpcListDownloadedModelsReturns


class PseudoSystemRpcListDownloadedModelsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoSystemRpcListDownloadedModels.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    returns: SystemRpcListDownloadedModelsReturns


class SystemRpcNotifyParameter(
    LMStudioStruct["SystemRpcNotifyParameterDict"], kw_only=True
):
    title: Title
    description: Description | None = None
    no_auto_dismiss: NoAutoDismiss | None = field(name="noAutoDismiss", default=None)


class SystemRpcNotifyParameterDict(TypedDict):
    """Corresponding typed dictionary definition for SystemRpcNotifyParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    title: str
    description: NotRequired[str | None]
    noAutoDismiss: NotRequired[bool | None]


class PseudoSystemRpcNotify(LMStudioStruct["PseudoSystemRpcNotifyDict"], kw_only=True):
    parameter: SystemRpcNotifyParameter


class PseudoSystemRpcNotifyDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoSystemRpcNotify.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: SystemRpcNotifyParameterDict


class PseudoSystem(LMStudioStruct["PseudoSystemDict"], kw_only=True):
    rpc_list_downloaded_models: PseudoSystemRpcListDownloadedModels = field(
        name="rpcListDownloadedModels"
    )
    rpc_notify: PseudoSystemRpcNotify = field(name="rpcNotify")
    rpc_version: PseudoSystemRpcVersion = field(name="rpcVersion")
    rpc_set_experiment_flag: PseudoSystemRpcSetExperimentFlag = field(
        name="rpcSetExperimentFlag"
    )
    rpc_get_experiment_flags: PseudoSystemRpcGetExperimentFlags = field(
        name="rpcGetExperimentFlags"
    )
    channel_alive: PseudoSystemChannelAlive = field(name="channelAlive")


class PseudoSystemDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoSystem.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    rpcListDownloadedModels: PseudoSystemRpcListDownloadedModelsDict
    rpcNotify: PseudoSystemRpcNotifyDict
    rpcVersion: PseudoSystemRpcVersionDict
    rpcSetExperimentFlag: PseudoSystemRpcSetExperimentFlagDict
    rpcGetExperimentFlags: PseudoSystemRpcGetExperimentFlagsDict
    channelAlive: PseudoSystemChannelAlive


class UserMessage(
    LMStudioStruct["UserMessageDict"], kw_only=True, tag_field="role", tag="user"
):
    role: ClassVar[Annotated[Literal["user"], Meta(title="Role")]] = "user"
    content: Sequence[TextData | FileHandle]


class UserMessageDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessageDataUser.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    role: Literal["user"]
    content: Sequence[TextDataDict | FileHandleDict]


class SystemPrompt(
    LMStudioStruct["SystemPromptDict"], kw_only=True, tag_field="role", tag="system"
):
    role: ClassVar[Annotated[Literal["system"], Meta(title="Role")]] = "system"
    content: Sequence[TextData | FileHandle]


class SystemPromptDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessageDataSystem.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    role: Literal["system"]
    content: Sequence[TextDataDict | FileHandleDict]


class ErrorDisplayDataGenericNoModelMatchingQuery(
    LMStudioStruct["ErrorDisplayDataGenericNoModelMatchingQueryDict"],
    kw_only=True,
    tag_field="code",
    tag="generic.noModelMatchingQuery",
):
    code: ClassVar[
        Annotated[Literal["generic.noModelMatchingQuery"], Meta(title="Code")]
    ] = "generic.noModelMatchingQuery"
    query: ModelQuery
    loaded_models_sample: Sequence[str] = field(name="loadedModelsSample")
    total_loaded_models: int = field(name="totalLoadedModels")


class ErrorDisplayDataGenericNoModelMatchingQueryDict(TypedDict):
    """Corresponding typed dictionary definition for ErrorDisplayDataGenericNoModelMatchingQuery.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    code: Literal["generic.noModelMatchingQuery"]
    query: ModelQueryDict
    loadedModelsSample: Sequence[str]
    totalLoadedModels: int


KvConfigFieldDependencyCondition = (
    KvConfigFieldDependencyConditionEquals | KvConfigFieldDependencyConditionNotEquals
)
KvConfigFieldDependencyConditionDict = (
    KvConfigFieldDependencyConditionEqualsDict
    | KvConfigFieldDependencyConditionNotEqualsDict
)


class Function(LMStudioStruct["FunctionDict"], kw_only=True):
    name: str
    description: str | None = None
    parameters: LlmToolParameters | None = None


class FunctionDict(TypedDict):
    """Corresponding typed dictionary definition for Function.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    name: str
    description: NotRequired[str | None]
    parameters: NotRequired[LlmToolParametersObjectDict | None]


class LlmToolFunction(LMStudioStruct["LlmToolFunctionDict"], kw_only=True):
    type: Annotated[Literal["function"], Meta(title="Type")]
    function: Function


class LlmToolFunctionDict(TypedDict):
    """Corresponding typed dictionary definition for LlmToolFunction.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["function"], Meta(title="Type")]
    function: FunctionDict


ProcessingRequestResponseConfirmToolCallResult = (
    ProcessingRequestResponseConfirmToolCallResultAllow
    | ProcessingRequestResponseConfirmToolCallResultDeny
)
ProcessingRequestResponseConfirmToolCallResultDict = (
    ProcessingRequestResponseConfirmToolCallResultAllowDict
    | ProcessingRequestResponseConfirmToolCallResultDenyDict
)


class ModelSpecifierQuery(
    LMStudioStruct["ModelSpecifierQueryDict"],
    kw_only=True,
    tag_field="type",
    tag="query",
):
    type: ClassVar[Annotated[Literal["query"], Meta(title="Type")]] = "query"
    query: ModelQuery


class ModelSpecifierQueryDict(TypedDict):
    """Corresponding typed dictionary definition for ModelSpecifierQuery.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["query"]
    query: ModelQueryDict


class DiagnosticsChannelStreamLogsToClientPacketLog(
    LMStudioStruct["DiagnosticsChannelStreamLogsToClientPacketLogDict"], kw_only=True
):
    type: Annotated[Literal["log"], Meta(title="Type")]
    log: DiagnosticsLogEvent


class DiagnosticsChannelStreamLogsToClientPacketLogDict(TypedDict):
    """Corresponding typed dictionary definition for DiagnosticsChannelStreamLogsToClientPacketLog.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Annotated[Literal["log"], Meta(title="Type")]
    log: DiagnosticsLogEventDict


EmbeddingRpcGetModelInfoReturnValue = EmbeddingModelInstanceInfo


class EmbeddingChannelLoadModelToClientPacketResolved(
    LMStudioStruct["EmbeddingChannelLoadModelToClientPacketResolvedDict"],
    kw_only=True,
    tag_field="type",
    tag="resolved",
):
    type: ClassVar[Annotated[Literal["resolved"], Meta(title="Type")]] = "resolved"
    info: EmbeddingModelInfo
    ambiguous: Sequence[str] | None = None


class EmbeddingChannelLoadModelToClientPacketResolvedDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelLoadModelToClientPacketResolved.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["resolved"]
    info: EmbeddingModelInfoDict
    ambiguous: NotRequired[Sequence[str] | None]


class EmbeddingChannelLoadModelToClientPacketSuccess(
    LMStudioStruct["EmbeddingChannelLoadModelToClientPacketSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="success",
):
    type: ClassVar[Annotated[Literal["success"], Meta(title="Type")]] = "success"
    info: EmbeddingModelInstanceInfo


class EmbeddingChannelLoadModelToClientPacketSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelLoadModelToClientPacketSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["success"]
    info: EmbeddingModelInstanceInfoDict


class EmbeddingChannelGetOrLoadToClientPacketAlreadyLoaded(
    LMStudioStruct["EmbeddingChannelGetOrLoadToClientPacketAlreadyLoadedDict"],
    kw_only=True,
    tag_field="type",
    tag="alreadyLoaded",
):
    type: ClassVar[Annotated[Literal["alreadyLoaded"], Meta(title="Type")]] = (
        "alreadyLoaded"
    )
    info: EmbeddingModelInstanceInfo


class EmbeddingChannelGetOrLoadToClientPacketAlreadyLoadedDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelGetOrLoadToClientPacketAlreadyLoaded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["alreadyLoaded"]
    info: EmbeddingModelInstanceInfoDict


class EmbeddingChannelGetOrLoadToClientPacketStartLoading(
    LMStudioStruct["EmbeddingChannelGetOrLoadToClientPacketStartLoadingDict"],
    kw_only=True,
    tag_field="type",
    tag="startLoading",
):
    type: ClassVar[Annotated[Literal["startLoading"], Meta(title="Type")]] = (
        "startLoading"
    )
    identifier: str
    info: EmbeddingModelInfo


class EmbeddingChannelGetOrLoadToClientPacketStartLoadingDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelGetOrLoadToClientPacketStartLoading.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["startLoading"]
    identifier: str
    info: EmbeddingModelInfoDict


class EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModel(
    LMStudioStruct["EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict"],
    kw_only=True,
    tag_field="type",
    tag="unloadingOtherJITModel",
):
    type: ClassVar[Annotated[Literal["unloadingOtherJITModel"], Meta(title="Type")]] = (
        "unloadingOtherJITModel"
    )
    info: ModelInstanceInfo


class EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["unloadingOtherJITModel"]
    info: ModelInstanceInfoDict


class EmbeddingChannelGetOrLoadToClientPacketLoadSuccess(
    LMStudioStruct["EmbeddingChannelGetOrLoadToClientPacketLoadSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="loadSuccess",
):
    type: ClassVar[Annotated[Literal["loadSuccess"], Meta(title="Type")]] = (
        "loadSuccess"
    )
    info: EmbeddingModelInstanceInfo


class EmbeddingChannelGetOrLoadToClientPacketLoadSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingChannelGetOrLoadToClientPacketLoadSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["loadSuccess"]
    info: EmbeddingModelInstanceInfoDict


LlmRpcGetModelInfoReturnValue = LlmInstanceInfo


class LlmChannelLoadModelToClientPacketResolved(
    LMStudioStruct["LlmChannelLoadModelToClientPacketResolvedDict"],
    kw_only=True,
    tag_field="type",
    tag="resolved",
):
    type: ClassVar[Annotated[Literal["resolved"], Meta(title="Type")]] = "resolved"
    info: LlmInfo
    ambiguous: Sequence[str] | None = None


class LlmChannelLoadModelToClientPacketResolvedDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelLoadModelToClientPacketResolved.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["resolved"]
    info: LlmInfoDict
    ambiguous: NotRequired[Sequence[str] | None]


class LlmChannelLoadModelToClientPacketSuccess(
    LMStudioStruct["LlmChannelLoadModelToClientPacketSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="success",
):
    type: ClassVar[Annotated[Literal["success"], Meta(title="Type")]] = "success"
    info: LlmInstanceInfo


class LlmChannelLoadModelToClientPacketSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelLoadModelToClientPacketSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["success"]
    info: LlmInstanceInfoDict


class LlmChannelGetOrLoadToClientPacketAlreadyLoaded(
    LMStudioStruct["LlmChannelGetOrLoadToClientPacketAlreadyLoadedDict"],
    kw_only=True,
    tag_field="type",
    tag="alreadyLoaded",
):
    type: ClassVar[Annotated[Literal["alreadyLoaded"], Meta(title="Type")]] = (
        "alreadyLoaded"
    )
    info: LlmInstanceInfo


class LlmChannelGetOrLoadToClientPacketAlreadyLoadedDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGetOrLoadToClientPacketAlreadyLoaded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["alreadyLoaded"]
    info: LlmInstanceInfoDict


class LlmChannelGetOrLoadToClientPacketStartLoading(
    LMStudioStruct["LlmChannelGetOrLoadToClientPacketStartLoadingDict"],
    kw_only=True,
    tag_field="type",
    tag="startLoading",
):
    type: ClassVar[Annotated[Literal["startLoading"], Meta(title="Type")]] = (
        "startLoading"
    )
    identifier: str
    info: LlmInfo


class LlmChannelGetOrLoadToClientPacketStartLoadingDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGetOrLoadToClientPacketStartLoading.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["startLoading"]
    identifier: str
    info: LlmInfoDict


class LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModel(
    LMStudioStruct["LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict"],
    kw_only=True,
    tag_field="type",
    tag="unloadingOtherJITModel",
):
    type: ClassVar[Annotated[Literal["unloadingOtherJITModel"], Meta(title="Type")]] = (
        "unloadingOtherJITModel"
    )
    info: ModelInstanceInfo


class LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["unloadingOtherJITModel"]
    info: ModelInstanceInfoDict


class LlmChannelGetOrLoadToClientPacketLoadSuccess(
    LMStudioStruct["LlmChannelGetOrLoadToClientPacketLoadSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="loadSuccess",
):
    type: ClassVar[Annotated[Literal["loadSuccess"], Meta(title="Type")]] = (
        "loadSuccess"
    )
    info: LlmInstanceInfo


class LlmChannelGetOrLoadToClientPacketLoadSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGetOrLoadToClientPacketLoadSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["loadSuccess"]
    info: LlmInstanceInfoDict


class LlmChannelPredictToClientPacketToolCallGenerationEnd(
    LMStudioStruct["LlmChannelPredictToClientPacketToolCallGenerationEndDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationEnd",
):
    type: ClassVar[Annotated[Literal["toolCallGenerationEnd"], Meta(title="Type")]] = (
        "toolCallGenerationEnd"
    )
    tool_call_request: ToolCallRequest = field(name="toolCallRequest")
    raw_content: str | None = field(name="rawContent", default=None)


class LlmChannelPredictToClientPacketToolCallGenerationEndDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketToolCallGenerationEnd.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationEnd"]
    toolCallRequest: ToolCallRequestDict
    rawContent: NotRequired[str | None]


class LlmChannelPredictToClientPacketSuccess(
    LMStudioStruct["LlmChannelPredictToClientPacketSuccessDict"],
    kw_only=True,
    tag_field="type",
    tag="success",
):
    type: ClassVar[Annotated[Literal["success"], Meta(title="Type")]] = "success"
    stats: LlmPredictionStats
    model_info: LlmInstanceInfo = field(name="modelInfo")
    load_model_config: LlmRpcGetLoadConfigReturns = field(name="loadModelConfig")
    prediction_config: LlmRpcGetLoadConfigReturns = field(name="predictionConfig")


class LlmChannelPredictToClientPacketSuccessDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictToClientPacketSuccess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["success"]
    stats: LlmPredictionStatsDict
    modelInfo: LlmInstanceInfoDict
    loadModelConfig: LlmRpcGetLoadConfigReturnsDict
    predictionConfig: LlmRpcGetLoadConfigReturnsDict


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEnd(
    LMStudioStruct[
        "LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEndDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationEnd",
):
    type: ClassVar[Annotated[Literal["toolCallGenerationEnd"], Meta(title="Type")]] = (
        "toolCallGenerationEnd"
    )
    tool_call_request: ToolCallRequest = field(name="toolCallRequest")


class LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEndDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEnd.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationEnd"]
    toolCallRequest: ToolCallRequestDict


class PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoop(
    LMStudioStruct[
        "PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoopDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="handlePredictionLoop",
):
    type: ClassVar[Annotated[Literal["handlePredictionLoop"], Meta(title="Type")]] = (
        "handlePredictionLoop"
    )
    task_id: str = field(name="taskId")
    config: LlmRpcGetLoadConfigReturns
    plugin_config: LlmRpcGetLoadConfigReturns = field(name="pluginConfig")
    global_plugin_config: LlmRpcGetLoadConfigReturns = field(name="globalPluginConfig")
    working_directory_path: str | None = field(name="workingDirectoryPath")
    pci: str
    token: str


class PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoopDict(
    TypedDict
):
    """Corresponding typed dictionary definition for PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoop.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["handlePredictionLoop"]
    taskId: str
    config: LlmRpcGetLoadConfigReturnsDict
    pluginConfig: LlmRpcGetLoadConfigReturnsDict
    globalPluginConfig: LlmRpcGetLoadConfigReturnsDict
    workingDirectoryPath: NotRequired[str | None]
    pci: str
    token: str


class PluginsChannelSetToolsProviderToClientPacketInitSession(
    LMStudioStruct["PluginsChannelSetToolsProviderToClientPacketInitSessionDict"],
    kw_only=True,
    tag_field="type",
    tag="initSession",
):
    type: ClassVar[Annotated[Literal["initSession"], Meta(title="Type")]] = (
        "initSession"
    )
    plugin_config: LlmRpcGetLoadConfigReturns = field(name="pluginConfig")
    global_plugin_config: LlmRpcGetLoadConfigReturns = field(name="globalPluginConfig")
    working_directory_path: str | None = field(name="workingDirectoryPath")
    session_id: str = field(name="sessionId")


class PluginsChannelSetToolsProviderToClientPacketInitSessionDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToClientPacketInitSession.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["initSession"]
    pluginConfig: LlmRpcGetLoadConfigReturnsDict
    globalPluginConfig: LlmRpcGetLoadConfigReturnsDict
    workingDirectoryPath: NotRequired[str | None]
    sessionId: str


class PluginsChannelSetGeneratorToServerPacketFragmentGenerated(
    LMStudioStruct["PluginsChannelSetGeneratorToServerPacketFragmentGeneratedDict"],
    kw_only=True,
    tag_field="type",
    tag="fragmentGenerated",
):
    type: ClassVar[Annotated[Literal["fragmentGenerated"], Meta(title="Type")]] = (
        "fragmentGenerated"
    )
    task_id: str = field(name="taskId")
    content: str
    opts: LlmPredictionFragmentInputOpts


class PluginsChannelSetGeneratorToServerPacketFragmentGeneratedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketFragmentGenerated.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["fragmentGenerated"]
    taskId: str
    content: str
    opts: LlmPredictionFragmentInputOptsDict


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationEnded(
    LMStudioStruct[
        "PluginsChannelSetGeneratorToServerPacketToolCallGenerationEndedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="toolCallGenerationEnded",
):
    type: ClassVar[
        Annotated[Literal["toolCallGenerationEnded"], Meta(title="Type")]
    ] = "toolCallGenerationEnded"
    task_id: str = field(name="taskId")
    tool_call_request: ToolCallRequest = field(name="toolCallRequest")


class PluginsChannelSetGeneratorToServerPacketToolCallGenerationEndedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToServerPacketToolCallGenerationEnded.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallGenerationEnded"]
    taskId: str
    toolCallRequest: ToolCallRequestDict


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdated(
    LMStudioStruct[
        "RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdatedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="planUpdated",
):
    type: ClassVar[Annotated[Literal["planUpdated"], Meta(title="Type")]] = (
        "planUpdated"
    )
    plan: ArtifactDownloadPlan


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdatedDict(
    TypedDict
):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdated.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["planUpdated"]
    plan: ArtifactDownloadPlanDict


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReady(
    LMStudioStruct[
        "RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReadyDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="planReady",
):
    type: ClassVar[Annotated[Literal["planReady"], Meta(title="Type")]] = "planReady"
    plan: ArtifactDownloadPlan


class RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReadyDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReady.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["planReady"]
    plan: ArtifactDownloadPlanDict


PromptTemplate = LlmPromptTemplate


class ArtifactModelDependency(
    LMStudioStruct["ArtifactModelDependencyDict"],
    kw_only=True,
    tag_field="type",
    tag="model",
):
    type: ClassVar[Annotated[Literal["model"], Meta(title="Type")]] = "model"
    purpose: ArtifactDependencyPurpose
    model_keys: Sequence[ModelKey] = field(name="modelKeys")
    sources: Sequence[ModelDownloadSource]


class ArtifactModelDependencyDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactModelDependency.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["model"]
    purpose: ArtifactDependencyPurpose
    modelKeys: Sequence[str]
    sources: Sequence[HuggingFaceModelDownloadSourceDict]


class ToolCallRequestData(
    LMStudioStruct["ToolCallRequestDataDict"],
    kw_only=True,
    tag_field="type",
    tag="toolCallRequest",
):
    type: ClassVar[Annotated[Literal["toolCallRequest"], Meta(title="Type")]] = (
        "toolCallRequest"
    )
    tool_call_request: ToolCallRequest = field(name="toolCallRequest")


class ToolCallRequestDataDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessagePartToolCallRequestData.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolCallRequest"]
    toolCallRequest: ToolCallRequestDict


class EmbeddingLoadModelConfig(
    LMStudioStruct["EmbeddingLoadModelConfigDict"], kw_only=True
):
    gpu: GpuSetting | None = None
    context_length: Annotated[int, Meta(ge=1)] | None = field(
        name="contextLength", default=None
    )
    rope_frequency_base: float | None = field(name="ropeFrequencyBase", default=None)
    rope_frequency_scale: float | None = field(name="ropeFrequencyScale", default=None)
    keep_model_in_memory: bool | None = field(name="keepModelInMemory", default=None)
    try_mmap: bool | None = field(name="tryMmap", default=None)


class EmbeddingLoadModelConfigDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingLoadModelConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    gpu: NotRequired[GpuSettingDict | None]
    contextLength: NotRequired[Annotated[int, Meta(ge=1)] | None]
    ropeFrequencyBase: NotRequired[float | None]
    ropeFrequencyScale: NotRequired[float | None]
    keepModelInMemory: NotRequired[bool | None]
    tryMmap: NotRequired[bool | None]


ErrorDisplayData = (
    ErrorDisplayDataGenericSpecificModelUnloaded
    | ErrorDisplayDataGenericNoModelMatchingQuery
    | ErrorDisplayDataGenericPathNotFound
    | ErrorDisplayDataGenericIdentifierNotFound
    | ErrorDisplayDataGenericDomainMismatch
    | ErrorDisplayDataGenericEngineDoesNotSupportFeature
    | ErrorDisplayDataGenericPresetNotFound
)
ErrorDisplayDataDict = (
    ErrorDisplayDataGenericPresetNotFoundDict
    | ErrorDisplayDataGenericEngineDoesNotSupportFeatureDict
    | ErrorDisplayDataGenericDomainMismatchDict
    | ErrorDisplayDataGenericIdentifierNotFoundDict
    | ErrorDisplayDataGenericPathNotFoundDict
    | ErrorDisplayDataGenericSpecificModelUnloadedDict
    | ErrorDisplayDataGenericNoModelMatchingQueryDict
)


class KvConfigFieldDependency(
    LMStudioStruct["KvConfigFieldDependencyDict"], kw_only=True
):
    key: str
    condition: KvConfigFieldDependencyCondition


class KvConfigFieldDependencyDict(TypedDict):
    """Corresponding typed dictionary definition for KvConfigFieldDependency.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    key: str
    condition: KvConfigFieldDependencyConditionDict


class LlmGenInfo(LMStudioStruct["LlmGenInfoDict"], kw_only=True):
    indexed_model_identifier: str = field(name="indexedModelIdentifier")
    identifier: str
    load_model_config: KvConfig = field(name="loadModelConfig")
    prediction_config: KvConfig = field(name="predictionConfig")
    stats: LlmPredictionStats


class LlmGenInfoDict(TypedDict):
    """Corresponding typed dictionary definition for LlmGenInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    indexedModelIdentifier: str
    identifier: str
    loadModelConfig: KvConfigDict
    predictionConfig: KvConfigDict
    stats: LlmPredictionStatsDict


LlmTool = LlmToolFunction


class ProcessingRequestResponseConfirmToolCall(
    LMStudioStruct["ProcessingRequestResponseConfirmToolCallDict"],
    kw_only=True,
    tag_field="type",
    tag="confirmToolCall",
):
    type: ClassVar[Annotated[Literal["confirmToolCall"], Meta(title="Type")]] = (
        "confirmToolCall"
    )
    result: ProcessingRequestResponseConfirmToolCallResult


class ProcessingRequestResponseConfirmToolCallDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingRequestResponseConfirmToolCall.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["confirmToolCall"]
    result: ProcessingRequestResponseConfirmToolCallResultDict


ProcessingRequestResponse = (
    ProcessingRequestResponseConfirmToolCall | ProcessingRequestResponseTextInput
)
ProcessingRequestResponseDict = (
    ProcessingRequestResponseConfirmToolCallDict
    | ProcessingRequestResponseTextInputDict
)


class ProcessingUpdateContentBlockAttachGenInfo(
    LMStudioStruct["ProcessingUpdateContentBlockAttachGenInfoDict"],
    kw_only=True,
    tag_field="type",
    tag="contentBlock.attachGenInfo",
):
    type: ClassVar[
        Annotated[Literal["contentBlock.attachGenInfo"], Meta(title="Type")]
    ] = "contentBlock.attachGenInfo"
    id: str
    gen_info: LlmGenInfo = field(name="genInfo")


class ProcessingUpdateContentBlockAttachGenInfoDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateContentBlockAttachGenInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["contentBlock.attachGenInfo"]
    id: str
    genInfo: LlmGenInfoDict


class ProcessingUpdateStatusCreate(
    LMStudioStruct["ProcessingUpdateStatusCreateDict"],
    kw_only=True,
    tag_field="type",
    tag="status.create",
):
    type: ClassVar[Annotated[Literal["status.create"], Meta(title="Type")]] = (
        "status.create"
    )
    id: str
    state: StatusStepState
    location: BlockLocation | None = None
    indentation: int | None = None


class ProcessingUpdateStatusCreateDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateStatusCreate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["status.create"]
    id: str
    state: StatusStepStateDict
    location: NotRequired[BlockLocationDict | None]
    indentation: NotRequired[int | None]


class ProcessingUpdateStatusUpdate(
    LMStudioStruct["ProcessingUpdateStatusUpdateDict"],
    kw_only=True,
    tag_field="type",
    tag="status.update",
):
    type: ClassVar[Annotated[Literal["status.update"], Meta(title="Type")]] = (
        "status.update"
    )
    id: str
    state: StatusStepState


class ProcessingUpdateStatusUpdateDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateStatusUpdate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["status.update"]
    id: str
    state: StatusStepStateDict


class ToolStatusStepState(LMStudioStruct["ToolStatusStepStateDict"], kw_only=True):
    status: ToolStatusStepStateStatus
    custom_status: str = field(name="customStatus")
    custom_warnings: Sequence[str] = field(name="customWarnings")


class ToolStatusStepStateDict(TypedDict):
    """Corresponding typed dictionary definition for ToolStatusStepState.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    status: ToolStatusStepStateStatusDict
    customStatus: str
    customWarnings: Sequence[str]


ModelSpecifier = ModelSpecifierQuery | ModelSpecifierInstanceReference
ModelSpecifierDict = ModelSpecifierQueryDict | ModelSpecifierInstanceReferenceDict


class ModelSearchResultEntryData(
    LMStudioStruct["ModelSearchResultEntryDataDict"], kw_only=True
):
    name: str
    identifier: ModelSearchResultIdentifier
    exact: bool | None = None
    staff_pick: bool | None = field(name="staffPick", default=None)


class ModelSearchResultEntryDataDict(TypedDict):
    """Corresponding typed dictionary definition for ModelSearchResultEntryData.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    name: str
    identifier: ModelSearchResultIdentifierDict
    exact: NotRequired[bool | None]
    staffPick: NotRequired[bool | None]


VirtualModelCustomFieldDefinition = (
    VirtualModelBooleanCustomFieldDefinition | VirtualModelStringCustomFieldDefinition
)
VirtualModelCustomFieldDefinitionDict = (
    VirtualModelBooleanCustomFieldDefinitionDict
    | VirtualModelStringCustomFieldDefinitionDict
)


class VirtualModelDefinition(
    LMStudioStruct["VirtualModelDefinitionDict"], kw_only=True
):
    model: Annotated[str, Meta(pattern="^[^/]+\\/[^/]+$")]
    base: str | Sequence[VirtualModelDefinitionConcreteModelBase]
    tags: Sequence[Tag] | None = None
    config: Config | None = None
    metadata_overrides: VirtualModelDefinitionMetadataOverrides | None = field(
        name="metadataOverrides", default=None
    )
    custom_fields: Sequence[VirtualModelCustomFieldDefinition] | None = field(
        name="customFields", default=None
    )
    suggestions: Sequence[VirtualModelSuggestion] | None = None


class VirtualModelDefinitionDict(TypedDict):
    """Corresponding typed dictionary definition for VirtualModelDefinition.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    model: Annotated[str, Meta(pattern="^[^/]+\\/[^/]+$")]
    base: str | Sequence[VirtualModelDefinitionConcreteModelBaseDict]
    tags: NotRequired[Sequence[str] | None]
    config: NotRequired[ConfigDict | None]
    metadataOverrides: NotRequired[VirtualModelDefinitionMetadataOverridesDict | None]
    customFields: NotRequired[Sequence[VirtualModelCustomFieldDefinitionDict] | None]
    suggestions: NotRequired[Sequence[VirtualModelSuggestionDict] | None]


DiagnosticsChannelStreamLogsToClientPacket = (
    DiagnosticsChannelStreamLogsToClientPacketLog
)


class PseudoDiagnosticsChannelStreamLogs(
    LMStudioStruct["PseudoDiagnosticsChannelStreamLogsDict"], kw_only=True
):
    to_client_packet: DiagnosticsChannelStreamLogsToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: DiagnosticsChannelStreamLogsToServerPacket = field(
        name="toServerPacket"
    )


class PseudoDiagnosticsChannelStreamLogsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoDiagnosticsChannelStreamLogs.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    toClientPacket: DiagnosticsChannelStreamLogsToClientPacketLogDict
    toServerPacket: DiagnosticsChannelStreamLogsToServerPacketStopDict


class PseudoDiagnostics(LMStudioStruct["PseudoDiagnosticsDict"], kw_only=True):
    channel_stream_logs: PseudoDiagnosticsChannelStreamLogs = field(
        name="channelStreamLogs"
    )


class PseudoDiagnosticsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoDiagnostics.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    channelStreamLogs: PseudoDiagnosticsChannelStreamLogsDict


class EmbeddingRpcGetModelInfoParameter(
    LMStudioStruct["EmbeddingRpcGetModelInfoParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    throw_if_not_found: bool = field(name="throwIfNotFound")


class EmbeddingRpcGetModelInfoParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcGetModelInfoParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    throwIfNotFound: bool


EmbeddingRpcGetModelInfoReturns = EmbeddingRpcGetModelInfoReturnValue | None
EmbeddingRpcGetModelInfoReturnsDict = EmbeddingModelInstanceInfoDict | None


class PseudoEmbeddingRpcGetModelInfo(
    LMStudioStruct["PseudoEmbeddingRpcGetModelInfoDict"], kw_only=True
):
    parameter: EmbeddingRpcGetModelInfoParameter
    returns: EmbeddingRpcGetModelInfoReturns | None = None


class PseudoEmbeddingRpcGetModelInfoDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingRpcGetModelInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: EmbeddingRpcGetModelInfoParameterDict
    returns: NotRequired[EmbeddingRpcGetModelInfoReturnsDict | None]


class EmbeddingRpcGetLoadConfigParameter(
    LMStudioStruct["EmbeddingRpcGetLoadConfigParameterDict"], kw_only=True
):
    specifier: ModelSpecifier


class EmbeddingRpcGetLoadConfigParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcGetLoadConfigParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict


class PseudoEmbeddingRpcGetLoadConfig(
    LMStudioStruct["PseudoEmbeddingRpcGetLoadConfigDict"], kw_only=True
):
    parameter: EmbeddingRpcGetLoadConfigParameter
    returns: EmbeddingRpcGetLoadConfigReturns


class PseudoEmbeddingRpcGetLoadConfigDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingRpcGetLoadConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: EmbeddingRpcGetLoadConfigParameterDict
    returns: EmbeddingRpcGetLoadConfigReturnsDict


class EmbeddingRpcEmbedStringParameter(
    LMStudioStruct["EmbeddingRpcEmbedStringParameterDict"], kw_only=True
):
    model_specifier: ModelSpecifier = field(name="modelSpecifier")
    input_string: str = field(name="inputString")


class EmbeddingRpcEmbedStringParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcEmbedStringParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelSpecifier: ModelSpecifierDict
    inputString: str


class PseudoEmbeddingRpcEmbedString(
    LMStudioStruct["PseudoEmbeddingRpcEmbedStringDict"], kw_only=True
):
    parameter: EmbeddingRpcEmbedStringParameter
    returns: EmbeddingRpcEmbedStringReturns


class PseudoEmbeddingRpcEmbedStringDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingRpcEmbedString.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: EmbeddingRpcEmbedStringParameterDict
    returns: EmbeddingRpcEmbedStringReturnsDict


class EmbeddingRpcTokenizeParameter(
    LMStudioStruct["EmbeddingRpcTokenizeParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    input_string: str = field(name="inputString")


class EmbeddingRpcTokenizeParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcTokenizeParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    inputString: str


class PseudoEmbeddingRpcTokenize(
    LMStudioStruct["PseudoEmbeddingRpcTokenizeDict"], kw_only=True
):
    parameter: EmbeddingRpcTokenizeParameter
    returns: EmbeddingRpcTokenizeReturns


class PseudoEmbeddingRpcTokenizeDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingRpcTokenize.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: EmbeddingRpcTokenizeParameterDict
    returns: EmbeddingRpcTokenizeReturnsDict


class EmbeddingRpcCountTokensParameter(
    LMStudioStruct["EmbeddingRpcCountTokensParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    input_string: str = field(name="inputString")


class EmbeddingRpcCountTokensParameterDict(TypedDict):
    """Corresponding typed dictionary definition for EmbeddingRpcCountTokensParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    inputString: str


class PseudoEmbeddingRpcCountTokens(
    LMStudioStruct["PseudoEmbeddingRpcCountTokensDict"], kw_only=True
):
    parameter: EmbeddingRpcCountTokensParameter
    returns: EmbeddingRpcCountTokensReturns


class PseudoEmbeddingRpcCountTokensDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingRpcCountTokens.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: EmbeddingRpcCountTokensParameterDict
    returns: EmbeddingRpcCountTokensReturnsDict


EmbeddingChannelLoadModelToClientPacket = (
    EmbeddingChannelLoadModelToClientPacketResolved
    | EmbeddingChannelLoadModelToClientPacketProgress
    | EmbeddingChannelLoadModelToClientPacketSuccess
)
EmbeddingChannelLoadModelToClientPacketDict = (
    EmbeddingChannelLoadModelToClientPacketSuccessDict
    | EmbeddingChannelLoadModelToClientPacketResolvedDict
    | EmbeddingChannelLoadModelToClientPacketProgressDict
)


class PseudoEmbeddingChannelLoadModel(
    LMStudioStruct["PseudoEmbeddingChannelLoadModelDict"], kw_only=True
):
    creation_parameter: EmbeddingChannelLoadModelCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: EmbeddingChannelLoadModelToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: EmbeddingChannelLoadModelToServerPacket = field(
        name="toServerPacket"
    )


class PseudoEmbeddingChannelLoadModelDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingChannelLoadModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: EmbeddingChannelLoadModelCreationParameterDict
    toClientPacket: EmbeddingChannelLoadModelToClientPacketDict
    toServerPacket: EmbeddingChannelLoadModelToServerPacketCancelDict


EmbeddingChannelGetOrLoadToClientPacket = (
    EmbeddingChannelGetOrLoadToClientPacketAlreadyLoaded
    | EmbeddingChannelGetOrLoadToClientPacketStartLoading
    | EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModel
    | EmbeddingChannelGetOrLoadToClientPacketLoadProgress
    | EmbeddingChannelGetOrLoadToClientPacketLoadSuccess
)
EmbeddingChannelGetOrLoadToClientPacketDict = (
    EmbeddingChannelGetOrLoadToClientPacketLoadSuccessDict
    | EmbeddingChannelGetOrLoadToClientPacketLoadProgressDict
    | EmbeddingChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict
    | EmbeddingChannelGetOrLoadToClientPacketAlreadyLoadedDict
    | EmbeddingChannelGetOrLoadToClientPacketStartLoadingDict
)


class PseudoEmbeddingChannelGetOrLoad(
    LMStudioStruct["PseudoEmbeddingChannelGetOrLoadDict"], kw_only=True
):
    creation_parameter: EmbeddingChannelGetOrLoadCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: EmbeddingChannelGetOrLoadToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: EmbeddingChannelGetOrLoadToServerPacket = field(
        name="toServerPacket"
    )


class PseudoEmbeddingChannelGetOrLoadDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbeddingChannelGetOrLoad.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: EmbeddingChannelGetOrLoadCreationParameterDict
    toClientPacket: EmbeddingChannelGetOrLoadToClientPacketDict
    toServerPacket: EmbeddingChannelGetOrLoadToServerPacketCancelDict


class PseudoEmbedding(LMStudioStruct["PseudoEmbeddingDict"], kw_only=True):
    rpc_unload_model: PseudoEmbeddingRpcUnloadModel = field(name="rpcUnloadModel")
    rpc_list_loaded: PseudoEmbeddingRpcListLoaded = field(name="rpcListLoaded")
    rpc_get_model_info: PseudoEmbeddingRpcGetModelInfo = field(name="rpcGetModelInfo")
    rpc_get_load_config: PseudoEmbeddingRpcGetLoadConfig = field(
        name="rpcGetLoadConfig"
    )
    rpc_embed_string: PseudoEmbeddingRpcEmbedString = field(name="rpcEmbedString")
    rpc_tokenize: PseudoEmbeddingRpcTokenize = field(name="rpcTokenize")
    rpc_count_tokens: PseudoEmbeddingRpcCountTokens = field(name="rpcCountTokens")
    channel_load_model: PseudoEmbeddingChannelLoadModel = field(name="channelLoadModel")
    channel_get_or_load: PseudoEmbeddingChannelGetOrLoad = field(
        name="channelGetOrLoad"
    )


class PseudoEmbeddingDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoEmbedding.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    rpcUnloadModel: PseudoEmbeddingRpcUnloadModelDict
    rpcListLoaded: PseudoEmbeddingRpcListLoadedDict
    rpcGetModelInfo: PseudoEmbeddingRpcGetModelInfoDict
    rpcGetLoadConfig: PseudoEmbeddingRpcGetLoadConfigDict
    rpcEmbedString: PseudoEmbeddingRpcEmbedStringDict
    rpcTokenize: PseudoEmbeddingRpcTokenizeDict
    rpcCountTokens: PseudoEmbeddingRpcCountTokensDict
    channelLoadModel: PseudoEmbeddingChannelLoadModelDict
    channelGetOrLoad: PseudoEmbeddingChannelGetOrLoadDict


class LlmRpcGetModelInfoParameter(
    LMStudioStruct["LlmRpcGetModelInfoParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    throw_if_not_found: bool = field(name="throwIfNotFound")


class LlmRpcGetModelInfoParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcGetModelInfoParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    throwIfNotFound: bool


LlmRpcGetModelInfoReturns = LlmRpcGetModelInfoReturnValue | None
LlmRpcGetModelInfoReturnsDict = LlmInstanceInfoDict | None


class PseudoLlmRpcGetModelInfo(
    LMStudioStruct["PseudoLlmRpcGetModelInfoDict"], kw_only=True
):
    parameter: LlmRpcGetModelInfoParameter
    returns: LlmRpcGetModelInfoReturns | None = None


class PseudoLlmRpcGetModelInfoDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcGetModelInfo.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: LlmRpcGetModelInfoParameterDict
    returns: NotRequired[LlmRpcGetModelInfoReturnsDict | None]


class LlmRpcGetLoadConfigParameter(
    LMStudioStruct["LlmRpcGetLoadConfigParameterDict"], kw_only=True
):
    specifier: ModelSpecifier


class LlmRpcGetLoadConfigParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcGetLoadConfigParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict


class PseudoLlmRpcGetLoadConfig(
    LMStudioStruct["PseudoLlmRpcGetLoadConfigDict"], kw_only=True
):
    parameter: LlmRpcGetLoadConfigParameter
    returns: LlmRpcGetLoadConfigReturns


class PseudoLlmRpcGetLoadConfigDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcGetLoadConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: LlmRpcGetLoadConfigParameterDict
    returns: LlmRpcGetLoadConfigReturnsDict


class LlmRpcTokenizeParameter(
    LMStudioStruct["LlmRpcTokenizeParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    input_string: str = field(name="inputString")


class LlmRpcTokenizeParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcTokenizeParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    inputString: str


class PseudoLlmRpcTokenize(LMStudioStruct["PseudoLlmRpcTokenizeDict"], kw_only=True):
    parameter: LlmRpcTokenizeParameter
    returns: LlmRpcTokenizeReturns


class PseudoLlmRpcTokenizeDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcTokenize.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: LlmRpcTokenizeParameterDict
    returns: LlmRpcTokenizeReturnsDict


class LlmRpcCountTokensParameter(
    LMStudioStruct["LlmRpcCountTokensParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    input_string: str = field(name="inputString")


class LlmRpcCountTokensParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcCountTokensParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    inputString: str


class PseudoLlmRpcCountTokens(
    LMStudioStruct["PseudoLlmRpcCountTokensDict"], kw_only=True
):
    parameter: LlmRpcCountTokensParameter
    returns: LlmRpcCountTokensReturns


class PseudoLlmRpcCountTokensDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcCountTokens.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: LlmRpcCountTokensParameterDict
    returns: LlmRpcCountTokensReturnsDict


class LlmRpcPreloadDraftModelParameter(
    LMStudioStruct["LlmRpcPreloadDraftModelParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    draft_model_key: str = field(name="draftModelKey")


class LlmRpcPreloadDraftModelParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcPreloadDraftModelParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    draftModelKey: str


class PseudoLlmRpcPreloadDraftModel(
    LMStudioStruct["PseudoLlmRpcPreloadDraftModelDict"], kw_only=True
):
    parameter: LlmRpcPreloadDraftModelParameter


class PseudoLlmRpcPreloadDraftModelDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcPreloadDraftModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: LlmRpcPreloadDraftModelParameterDict


LlmChannelLoadModelToClientPacket = (
    LlmChannelLoadModelToClientPacketResolved
    | LlmChannelLoadModelToClientPacketProgress
    | LlmChannelLoadModelToClientPacketSuccess
)
LlmChannelLoadModelToClientPacketDict = (
    LlmChannelLoadModelToClientPacketSuccessDict
    | LlmChannelLoadModelToClientPacketResolvedDict
    | LlmChannelLoadModelToClientPacketProgressDict
)


class PseudoLlmChannelLoadModel(
    LMStudioStruct["PseudoLlmChannelLoadModelDict"], kw_only=True
):
    creation_parameter: LlmChannelLoadModelCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: LlmChannelLoadModelToClientPacket = field(name="toClientPacket")
    to_server_packet: LlmChannelLoadModelToServerPacket = field(name="toServerPacket")


class PseudoLlmChannelLoadModelDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmChannelLoadModel.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: LlmChannelLoadModelCreationParameterDict
    toClientPacket: LlmChannelLoadModelToClientPacketDict
    toServerPacket: LlmChannelLoadModelToServerPacketCancelDict


LlmChannelGetOrLoadToClientPacket = (
    LlmChannelGetOrLoadToClientPacketAlreadyLoaded
    | LlmChannelGetOrLoadToClientPacketStartLoading
    | LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModel
    | LlmChannelGetOrLoadToClientPacketLoadProgress
    | LlmChannelGetOrLoadToClientPacketLoadSuccess
)
LlmChannelGetOrLoadToClientPacketDict = (
    LlmChannelGetOrLoadToClientPacketLoadSuccessDict
    | LlmChannelGetOrLoadToClientPacketLoadProgressDict
    | LlmChannelGetOrLoadToClientPacketUnloadingOtherJITModelDict
    | LlmChannelGetOrLoadToClientPacketAlreadyLoadedDict
    | LlmChannelGetOrLoadToClientPacketStartLoadingDict
)


class PseudoLlmChannelGetOrLoad(
    LMStudioStruct["PseudoLlmChannelGetOrLoadDict"], kw_only=True
):
    creation_parameter: LlmChannelGetOrLoadCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: LlmChannelGetOrLoadToClientPacket = field(name="toClientPacket")
    to_server_packet: LlmChannelGetOrLoadToServerPacket = field(name="toServerPacket")


class PseudoLlmChannelGetOrLoadDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmChannelGetOrLoad.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: LlmChannelGetOrLoadCreationParameterDict
    toClientPacket: LlmChannelGetOrLoadToClientPacketDict
    toServerPacket: LlmChannelGetOrLoadToServerPacketCancelDict


LlmChannelPredictToClientPacket = (
    LlmChannelPredictToClientPacketFragment
    | LlmChannelPredictToClientPacketPromptProcessingProgress
    | LlmChannelPredictToClientPacketToolCallGenerationStart
    | LlmChannelPredictToClientPacketToolCallGenerationNameReceived
    | LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGenerated
    | LlmChannelPredictToClientPacketToolCallGenerationEnd
    | LlmChannelPredictToClientPacketToolCallGenerationFailed
    | LlmChannelPredictToClientPacketSuccess
)
LlmChannelPredictToClientPacketDict = (
    LlmChannelPredictToClientPacketSuccessDict
    | LlmChannelPredictToClientPacketToolCallGenerationFailedDict
    | LlmChannelPredictToClientPacketToolCallGenerationEndDict
    | LlmChannelPredictToClientPacketToolCallGenerationArgumentFragmentGeneratedDict
    | LlmChannelPredictToClientPacketToolCallGenerationNameReceivedDict
    | LlmChannelPredictToClientPacketToolCallGenerationStartDict
    | LlmChannelPredictToClientPacketFragmentDict
    | LlmChannelPredictToClientPacketPromptProcessingProgressDict
)
LlmChannelGenerateWithGeneratorToClientPacket = (
    LlmChannelGenerateWithGeneratorToClientPacketFragment
    | LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgress
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStart
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceived
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGenerated
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEnd
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailed
    | LlmChannelGenerateWithGeneratorToClientPacketSuccess
)
LlmChannelGenerateWithGeneratorToClientPacketDict = (
    LlmChannelGenerateWithGeneratorToClientPacketSuccessDict
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationFailedDict
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationEndDict
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationArgumentFragmentGeneratedDict
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationNameReceivedDict
    | LlmChannelGenerateWithGeneratorToClientPacketToolCallGenerationStartDict
    | LlmChannelGenerateWithGeneratorToClientPacketFragmentDict
    | LlmChannelGenerateWithGeneratorToClientPacketPromptProcessingProgressDict
)


class PluginsRpcProcessingHandleRequestReturns(
    LMStudioStruct["PluginsRpcProcessingHandleRequestReturnsDict"], kw_only=True
):
    response: ProcessingRequestResponse


class PluginsRpcProcessingHandleRequestReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingHandleRequestReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    response: ProcessingRequestResponseDict


class PseudoPluginsRpcProcessingHandleRequest(
    LMStudioStruct["PseudoPluginsRpcProcessingHandleRequestDict"], kw_only=True
):
    parameter: PluginsRpcProcessingHandleRequestParameter
    returns: PluginsRpcProcessingHandleRequestReturns


class PseudoPluginsRpcProcessingHandleRequestDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingHandleRequest.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingHandleRequestParameterDict
    returns: PluginsRpcProcessingHandleRequestReturnsDict


PluginsChannelSetPredictionLoopHandlerToClientPacket = (
    PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoop
    | PluginsChannelSetPredictionLoopHandlerToClientPacketAbort
)
PluginsChannelSetPredictionLoopHandlerToClientPacketDict = (
    PluginsChannelSetPredictionLoopHandlerToClientPacketHandlePredictionLoopDict
    | PluginsChannelSetPredictionLoopHandlerToClientPacketAbortDict
)


class PseudoPluginsChannelSetPredictionLoopHandler(
    LMStudioStruct["PseudoPluginsChannelSetPredictionLoopHandlerDict"], kw_only=True
):
    to_client_packet: PluginsChannelSetPredictionLoopHandlerToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: PluginsChannelSetPredictionLoopHandlerToServerPacket = field(
        name="toServerPacket"
    )


class PseudoPluginsChannelSetPredictionLoopHandlerDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsChannelSetPredictionLoopHandler.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    toClientPacket: PluginsChannelSetPredictionLoopHandlerToClientPacketDict
    toServerPacket: PluginsChannelSetPredictionLoopHandlerToServerPacketDict


PluginsChannelSetToolsProviderToClientPacket = (
    PluginsChannelSetToolsProviderToClientPacketInitSession
    | PluginsChannelSetToolsProviderToClientPacketDiscardSession
    | PluginsChannelSetToolsProviderToClientPacketCallTool
    | PluginsChannelSetToolsProviderToClientPacketAbortToolCall
)
PluginsChannelSetToolsProviderToClientPacketDict = (
    PluginsChannelSetToolsProviderToClientPacketAbortToolCallDict
    | PluginsChannelSetToolsProviderToClientPacketCallToolDict
    | PluginsChannelSetToolsProviderToClientPacketInitSessionDict
    | PluginsChannelSetToolsProviderToClientPacketDiscardSessionDict
)
PluginsChannelSetGeneratorToServerPacket = (
    PluginsChannelSetGeneratorToServerPacketComplete
    | PluginsChannelSetGeneratorToServerPacketAborted
    | PluginsChannelSetGeneratorToServerPacketError
    | PluginsChannelSetGeneratorToServerPacketFragmentGenerated
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationStarted
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceived
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGenerated
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationEnded
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailed
)
PluginsChannelSetGeneratorToServerPacketDict = (
    PluginsChannelSetGeneratorToServerPacketToolCallGenerationFailedDict
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationEndedDict
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationArgumentFragmentGeneratedDict
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationNameReceivedDict
    | PluginsChannelSetGeneratorToServerPacketToolCallGenerationStartedDict
    | PluginsChannelSetGeneratorToServerPacketFragmentGeneratedDict
    | PluginsChannelSetGeneratorToServerPacketErrorDict
    | PluginsChannelSetGeneratorToServerPacketCompleteDict
    | PluginsChannelSetGeneratorToServerPacketAbortedDict
)


class RepositoryRpcSearchModelsReturns(
    LMStudioStruct["RepositoryRpcSearchModelsReturnsDict"], kw_only=True
):
    results: Sequence[ModelSearchResultEntryData]


class RepositoryRpcSearchModelsReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for RepositoryRpcSearchModelsReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    results: Sequence[ModelSearchResultEntryDataDict]


class PseudoRepositoryRpcSearchModels(
    LMStudioStruct["PseudoRepositoryRpcSearchModelsDict"], kw_only=True
):
    parameter: RepositoryRpcSearchModelsParameter
    returns: RepositoryRpcSearchModelsReturns


class PseudoRepositoryRpcSearchModelsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryRpcSearchModels.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: RepositoryRpcSearchModelsParameterDict
    returns: RepositoryRpcSearchModelsReturnsDict


RepositoryChannelCreateArtifactDownloadPlanToClientPacket = (
    RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdated
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReady
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgress
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizing
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccess
)
RepositoryChannelCreateArtifactDownloadPlanToClientPacketDict = (
    RepositoryChannelCreateArtifactDownloadPlanToClientPacketSuccessDict
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketStartFinalizingDict
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketDownloadProgressDict
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanUpdatedDict
    | RepositoryChannelCreateArtifactDownloadPlanToClientPacketPlanReadyDict
)


class PseudoRepositoryChannelCreateArtifactDownloadPlan(
    LMStudioStruct["PseudoRepositoryChannelCreateArtifactDownloadPlanDict"],
    kw_only=True,
):
    creation_parameter: RepositoryChannelCreateArtifactDownloadPlanCreationParameter = (
        field(name="creationParameter")
    )
    to_client_packet: RepositoryChannelCreateArtifactDownloadPlanToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: RepositoryChannelCreateArtifactDownloadPlanToServerPacket = field(
        name="toServerPacket"
    )


class PseudoRepositoryChannelCreateArtifactDownloadPlanDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepositoryChannelCreateArtifactDownloadPlan.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: RepositoryChannelCreateArtifactDownloadPlanCreationParameterDict
    toClientPacket: RepositoryChannelCreateArtifactDownloadPlanToClientPacketDict
    toServerPacket: RepositoryChannelCreateArtifactDownloadPlanToServerPacketDict


class PseudoRepository(LMStudioStruct["PseudoRepositoryDict"], kw_only=True):
    rpc_search_models: PseudoRepositoryRpcSearchModels = field(name="rpcSearchModels")
    rpc_get_model_download_options: PseudoRepositoryRpcGetModelDownloadOptions = field(
        name="rpcGetModelDownloadOptions"
    )
    rpc_install_plugin_dependencies: PseudoRepositoryRpcInstallPluginDependencies = (
        field(name="rpcInstallPluginDependencies")
    )
    rpc_get_local_artifact_files: PseudoRepositoryRpcGetLocalArtifactFiles = field(
        name="rpcGetLocalArtifactFiles"
    )
    rpc_login_with_pre_authenticated_keys: PseudoRepositoryRpcLoginWithPreAuthenticatedKeys = field(
        name="rpcLoginWithPreAuthenticatedKeys"
    )
    channel_download_model: PseudoRepositoryChannelDownloadModel = field(
        name="channelDownloadModel"
    )
    channel_download_artifact: PseudoRepositoryChannelDownloadArtifact = field(
        name="channelDownloadArtifact"
    )
    channel_push_artifact: PseudoRepositoryChannelPushArtifact = field(
        name="channelPushArtifact"
    )
    channel_ensure_authenticated: PseudoRepositoryChannelEnsureAuthenticated = field(
        name="channelEnsureAuthenticated"
    )
    channel_create_artifact_download_plan: PseudoRepositoryChannelCreateArtifactDownloadPlan = field(
        name="channelCreateArtifactDownloadPlan"
    )


class PseudoRepositoryDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoRepository.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    rpcSearchModels: PseudoRepositoryRpcSearchModelsDict
    rpcGetModelDownloadOptions: PseudoRepositoryRpcGetModelDownloadOptionsDict
    rpcInstallPluginDependencies: PseudoRepositoryRpcInstallPluginDependenciesDict
    rpcGetLocalArtifactFiles: PseudoRepositoryRpcGetLocalArtifactFilesDict
    rpcLoginWithPreAuthenticatedKeys: (
        PseudoRepositoryRpcLoginWithPreAuthenticatedKeysDict
    )
    channelDownloadModel: PseudoRepositoryChannelDownloadModelDict
    channelDownloadArtifact: PseudoRepositoryChannelDownloadArtifactDict
    channelPushArtifact: PseudoRepositoryChannelPushArtifactDict
    channelEnsureAuthenticated: PseudoRepositoryChannelEnsureAuthenticatedDict
    channelCreateArtifactDownloadPlan: (
        PseudoRepositoryChannelCreateArtifactDownloadPlanDict
    )


class AssistantResponse(
    LMStudioStruct["AssistantResponseDict"],
    kw_only=True,
    tag_field="role",
    tag="assistant",
):
    role: ClassVar[Annotated[Literal["assistant"], Meta(title="Role")]] = "assistant"
    content: Sequence[TextData | FileHandle | ToolCallRequestData]


class AssistantResponseDict(TypedDict):
    """Corresponding typed dictionary definition for ChatMessageDataAssistant.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    role: Literal["assistant"]
    content: Sequence[TextDataDict | FileHandleDict | ToolCallRequestDataDict]


class LlmToolUseSettingToolArray(
    LMStudioStruct["LlmToolUseSettingToolArrayDict"],
    kw_only=True,
    tag_field="type",
    tag="toolArray",
):
    type: ClassVar[Annotated[Literal["toolArray"], Meta(title="Type")]] = "toolArray"
    tools: Sequence[LlmTool] | None = None
    force: bool | None = None


class LlmToolUseSettingToolArrayDict(TypedDict):
    """Corresponding typed dictionary definition for LlmToolUseSettingToolArray.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolArray"]
    tools: NotRequired[Sequence[LlmToolFunctionDict] | None]
    force: NotRequired[bool | None]


class PluginsChannelSetToolsProviderToServerPacketSessionInitialized(
    LMStudioStruct[
        "PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict"
    ],
    kw_only=True,
    tag_field="type",
    tag="sessionInitialized",
):
    type: ClassVar[Annotated[Literal["sessionInitialized"], Meta(title="Type")]] = (
        "sessionInitialized"
    )
    session_id: str = field(name="sessionId")
    tool_definitions: Sequence[LlmTool] = field(name="toolDefinitions")


class PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetToolsProviderToServerPacketSessionInitialized.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["sessionInitialized"]
    sessionId: str
    toolDefinitions: Sequence[LlmToolFunctionDict]


ArtifactDependency = ArtifactModelDependency | ArtifactArtifactDependency
ArtifactDependencyDict = ArtifactModelDependencyDict | ArtifactArtifactDependencyDict


class ArtifactManifestBase(LMStudioStruct["ArtifactManifestBaseDict"], kw_only=True):
    owner: KebabCase
    name: Annotated[
        str, Meta(max_length=100, min_length=1, pattern="^[a-z0-9]+(?:[-.][a-z0-9]+)*$")
    ]
    revision: int | None = None
    dependencies: Sequence[ArtifactDependency] | None = None
    tags: Sequence[str] | None = None


class ArtifactManifestBaseDict(TypedDict):
    """Corresponding typed dictionary definition for ArtifactManifestBase.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    owner: str
    name: Annotated[
        str, Meta(max_length=100, min_length=1, pattern="^[a-z0-9]+(?:[-.][a-z0-9]+)*$")
    ]
    revision: NotRequired[int | None]
    dependencies: NotRequired[Sequence[ArtifactDependencyDict] | None]
    tags: NotRequired[Sequence[str] | None]


AnyChatMessage = AssistantResponse | UserMessage | SystemPrompt | ToolResultMessage
AnyChatMessageDict = (
    ToolResultMessageDict | SystemPromptDict | AssistantResponseDict | UserMessageDict
)
ChatMessagePartData = TextData | FileHandle | ToolCallRequestData | ToolCallResultData
ChatMessagePartDataDict = (
    ToolCallResultDataDict | ToolCallRequestDataDict | TextDataDict | FileHandleDict
)


class LlmApplyPromptTemplateOpts(
    LMStudioStruct["LlmApplyPromptTemplateOptsDict"], kw_only=True
):
    omit_bos_token: bool | None = field(name="omitBosToken", default=None)
    omit_eos_token: bool | None = field(name="omitEosToken", default=None)
    tool_definitions: Sequence[LlmTool] | None = field(
        name="toolDefinitions", default=None
    )


class LlmApplyPromptTemplateOptsDict(TypedDict):
    """Corresponding typed dictionary definition for LlmApplyPromptTemplateOpts.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    omitBosToken: NotRequired[bool | None]
    omitEosToken: NotRequired[bool | None]
    toolDefinitions: NotRequired[Sequence[LlmToolFunctionDict] | None]


LlmToolArray = Sequence[LlmTool]
LlmToolUseSetting = LlmToolUseSettingNone | LlmToolUseSettingToolArray
LlmToolUseSettingDict = LlmToolUseSettingNoneDict | LlmToolUseSettingToolArrayDict
PreprocessorUpdate = (
    ProcessingUpdateStatusCreate
    | ProcessingUpdateStatusUpdate
    | ProcessingUpdateStatusRemove
    | ProcessingUpdateCitationBlockCreate
    | ProcessingUpdateDebugInfoBlockCreate
)
PreprocessorUpdateDict = (
    ProcessingUpdateDebugInfoBlockCreateDict
    | ProcessingUpdateCitationBlockCreateDict
    | ProcessingUpdateStatusRemoveDict
    | ProcessingUpdateStatusCreateDict
    | ProcessingUpdateStatusUpdateDict
)


class ProcessingUpdateToolStatusCreate(
    LMStudioStruct["ProcessingUpdateToolStatusCreateDict"],
    kw_only=True,
    tag_field="type",
    tag="toolStatus.create",
):
    type: ClassVar[Annotated[Literal["toolStatus.create"], Meta(title="Type")]] = (
        "toolStatus.create"
    )
    id: str
    call_id: int = field(name="callId")
    state: ToolStatusStepState


class ProcessingUpdateToolStatusCreateDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateToolStatusCreate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolStatus.create"]
    id: str
    callId: int
    state: ToolStatusStepStateDict


class ProcessingUpdateToolStatusUpdate(
    LMStudioStruct["ProcessingUpdateToolStatusUpdateDict"],
    kw_only=True,
    tag_field="type",
    tag="toolStatus.update",
):
    type: ClassVar[Annotated[Literal["toolStatus.update"], Meta(title="Type")]] = (
        "toolStatus.update"
    )
    id: str
    state: ToolStatusStepState


class ProcessingUpdateToolStatusUpdateDict(TypedDict):
    """Corresponding typed dictionary definition for ProcessingUpdateToolStatusUpdate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["toolStatus.update"]
    id: str
    state: ToolStatusStepStateDict


PluginsChannelSetToolsProviderToServerPacket = (
    PluginsChannelSetToolsProviderToServerPacketSessionInitialized
    | PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailed
    | PluginsChannelSetToolsProviderToServerPacketToolCallComplete
    | PluginsChannelSetToolsProviderToServerPacketToolCallError
    | PluginsChannelSetToolsProviderToServerPacketToolCallStatus
    | PluginsChannelSetToolsProviderToServerPacketToolCallWarn
)
PluginsChannelSetToolsProviderToServerPacketDict = (
    PluginsChannelSetToolsProviderToServerPacketToolCallWarnDict
    | PluginsChannelSetToolsProviderToServerPacketToolCallStatusDict
    | PluginsChannelSetToolsProviderToServerPacketToolCallErrorDict
    | PluginsChannelSetToolsProviderToServerPacketToolCallCompleteDict
    | PluginsChannelSetToolsProviderToServerPacketSessionInitializedDict
    | PluginsChannelSetToolsProviderToServerPacketSessionInitializationFailedDict
)


class PseudoPluginsChannelSetToolsProvider(
    LMStudioStruct["PseudoPluginsChannelSetToolsProviderDict"], kw_only=True
):
    to_client_packet: PluginsChannelSetToolsProviderToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: PluginsChannelSetToolsProviderToServerPacket = field(
        name="toServerPacket"
    )


class PseudoPluginsChannelSetToolsProviderDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsChannelSetToolsProvider.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    toClientPacket: PluginsChannelSetToolsProviderToClientPacketDict
    toServerPacket: PluginsChannelSetToolsProviderToServerPacketDict


class PluginsChannelSetPreprocessorToClientPacketPreprocess(
    LMStudioStruct["PluginsChannelSetPreprocessorToClientPacketPreprocessDict"],
    kw_only=True,
    tag_field="type",
    tag="preprocess",
):
    type: ClassVar[Annotated[Literal["preprocess"], Meta(title="Type")]] = "preprocess"
    task_id: str = field(name="taskId")
    input: AnyChatMessage
    config: LlmRpcGetLoadConfigReturns
    plugin_config: LlmRpcGetLoadConfigReturns = field(name="pluginConfig")
    global_plugin_config: LlmRpcGetLoadConfigReturns = field(name="globalPluginConfig")
    working_directory_path: str | None = field(name="workingDirectoryPath")
    pci: str
    token: str


class PluginsChannelSetPreprocessorToClientPacketPreprocessDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPreprocessorToClientPacketPreprocess.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["preprocess"]
    taskId: str
    input: AnyChatMessageDict
    config: LlmRpcGetLoadConfigReturnsDict
    pluginConfig: LlmRpcGetLoadConfigReturnsDict
    globalPluginConfig: LlmRpcGetLoadConfigReturnsDict
    workingDirectoryPath: NotRequired[str | None]
    pci: str
    token: str


class PluginsChannelSetPreprocessorToServerPacketComplete(
    LMStudioStruct["PluginsChannelSetPreprocessorToServerPacketCompleteDict"],
    kw_only=True,
    tag_field="type",
    tag="complete",
):
    type: ClassVar[Annotated[Literal["complete"], Meta(title="Type")]] = "complete"
    task_id: str = field(name="taskId")
    processed: AnyChatMessage


class PluginsChannelSetPreprocessorToServerPacketCompleteDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetPreprocessorToServerPacketComplete.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["complete"]
    taskId: str
    processed: AnyChatMessageDict


Dependencies = Sequence[ArtifactDependency]
Messages = Sequence[AnyChatMessage]
RawTools = LlmToolUseSetting


class ChatHistoryData(LMStudioStruct["ChatHistoryDataDict"], kw_only=True):
    messages: Sequence[AnyChatMessage]


class ChatHistoryDataDict(TypedDict):
    """Corresponding typed dictionary definition for ChatHistoryData.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    messages: Sequence[AnyChatMessageDict]


class LlmPredictionConfigInput(
    LMStudioStruct["LlmPredictionConfigInputDict"], kw_only=True
):
    max_tokens: Any | MaxTokens | bool | None = field(name="maxTokens", default=None)
    temperature: Annotated[float, Meta(ge=0.0)] | None = None
    stop_strings: Sequence[str] | None = field(name="stopStrings", default=None)
    tool_call_stop_strings: Sequence[str] | None = field(
        name="toolCallStopStrings", default=None
    )
    context_overflow_policy: LlmContextOverflowPolicy | None = field(
        name="contextOverflowPolicy", default=None
    )
    structured: ZodSchema | LlmStructuredPredictionSetting | None = None
    raw_tools: LlmToolUseSetting | None = field(name="rawTools", default=None)
    top_k_sampling: float | None = field(name="topKSampling", default=None)
    repeat_penalty: Any | float | bool | None = field(
        name="repeatPenalty", default=None
    )
    min_p_sampling: Any | float | bool | None = field(name="minPSampling", default=None)
    top_p_sampling: Any | float | bool | None = field(name="topPSampling", default=None)
    cpu_threads: int | None = field(name="cpuThreads", default=None)
    prompt_template: LlmPromptTemplate | None = field(
        name="promptTemplate", default=None
    )
    draft_model: str | None = field(name="draftModel", default=None)
    speculative_decoding_num_draft_tokens_exact: Annotated[int, Meta(ge=1)] | None = (
        field(name="speculativeDecodingNumDraftTokensExact", default=None)
    )
    speculative_decoding_min_draft_length_to_consider: (
        Annotated[int, Meta(ge=0)] | None
    ) = field(name="speculativeDecodingMinDraftLengthToConsider", default=None)
    speculative_decoding_min_continue_drafting_probability: float | None = field(
        name="speculativeDecodingMinContinueDraftingProbability", default=None
    )
    reasoning_parsing: LlmReasoningParsing | None = field(
        name="reasoningParsing", default=None
    )
    raw: KvConfig | None = None


class LlmPredictionConfigInputDict(TypedDict):
    """Corresponding typed dictionary definition for LlmPredictionConfigInput.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    maxTokens: NotRequired[Any | int | bool | None]
    temperature: NotRequired[Annotated[float, Meta(ge=0.0)] | None]
    stopStrings: NotRequired[Sequence[str] | None]
    toolCallStopStrings: NotRequired[Sequence[str] | None]
    contextOverflowPolicy: NotRequired[LlmContextOverflowPolicy | None]
    structured: NotRequired[ZodSchema | LlmStructuredPredictionSettingDict | None]
    rawTools: NotRequired[LlmToolUseSettingDict | None]
    topKSampling: NotRequired[float | None]
    repeatPenalty: NotRequired[Any | float | bool | None]
    minPSampling: NotRequired[Any | float | bool | None]
    topPSampling: NotRequired[Any | float | bool | None]
    cpuThreads: NotRequired[int | None]
    promptTemplate: NotRequired[LlmPromptTemplateDict | None]
    draftModel: NotRequired[str | None]
    speculativeDecodingNumDraftTokensExact: NotRequired[
        Annotated[int, Meta(ge=1)] | None
    ]
    speculativeDecodingMinDraftLengthToConsider: NotRequired[
        Annotated[int, Meta(ge=0)] | None
    ]
    speculativeDecodingMinContinueDraftingProbability: NotRequired[float | None]
    reasoningParsing: NotRequired[LlmReasoningParsingDict | None]
    raw: NotRequired[KvConfigDict | None]


class LlmPredictionConfig(LMStudioStruct["LlmPredictionConfigDict"], kw_only=True):
    max_tokens: MaxTokensModel | None = field(name="maxTokens", default=None)
    temperature: Temperature | None = None
    stop_strings: StopStrings | None = field(name="stopStrings", default=None)
    tool_call_stop_strings: ToolCallStopStrings | None = field(
        name="toolCallStopStrings", default=None
    )
    context_overflow_policy: ContextOverflowPolicy | None = field(
        name="contextOverflowPolicy", default=None
    )
    structured: LlmStructuredPredictionSetting | None = None
    raw_tools: RawTools | None = field(name="rawTools", default=None)
    top_k_sampling: TopKSampling | None = field(name="topKSampling", default=None)
    repeat_penalty: RepeatPenalty | None = field(name="repeatPenalty", default=None)
    min_p_sampling: MinPSampling | None = field(name="minPSampling", default=None)
    top_p_sampling: TopPSampling | None = field(name="topPSampling", default=None)
    cpu_threads: CpuThreads | None = field(name="cpuThreads", default=None)
    prompt_template: PromptTemplate | None = field(name="promptTemplate", default=None)
    draft_model: DraftModel | None = field(name="draftModel", default=None)
    speculative_decoding_num_draft_tokens_exact: (
        SpeculativeDecodingNumDraftTokensExact | None
    ) = field(name="speculativeDecodingNumDraftTokensExact", default=None)
    speculative_decoding_min_draft_length_to_consider: (
        SpeculativeDecodingMinDraftLengthToConsider | None
    ) = field(name="speculativeDecodingMinDraftLengthToConsider", default=None)
    speculative_decoding_min_continue_drafting_probability: (
        SpeculativeDecodingMinContinueDraftingProbability | None
    ) = field(name="speculativeDecodingMinContinueDraftingProbability", default=None)
    reasoning_parsing: ReasoningParsing | None = field(
        name="reasoningParsing", default=None
    )
    raw: Raw | None = None


class LlmPredictionConfigDict(TypedDict):
    """Corresponding typed dictionary definition for LlmPredictionConfig.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    maxTokens: NotRequired[MaxTokensModelDict | None]
    temperature: NotRequired[float | None]
    stopStrings: NotRequired[StopStrings | None]
    toolCallStopStrings: NotRequired[ToolCallStopStrings | None]
    contextOverflowPolicy: NotRequired[ContextOverflowPolicy | None]
    structured: NotRequired[LlmStructuredPredictionSettingDict | None]
    rawTools: NotRequired[LlmToolUseSettingDict | None]
    topKSampling: NotRequired[float | None]
    repeatPenalty: NotRequired[RepeatPenalty | None]
    minPSampling: NotRequired[MinPSampling | None]
    topPSampling: NotRequired[TopPSampling | None]
    cpuThreads: NotRequired[int | None]
    promptTemplate: NotRequired[LlmPromptTemplateDict | None]
    draftModel: NotRequired[str | None]
    speculativeDecodingNumDraftTokensExact: NotRequired[int | None]
    speculativeDecodingMinDraftLengthToConsider: NotRequired[int | None]
    speculativeDecodingMinContinueDraftingProbability: NotRequired[float | None]
    reasoningParsing: NotRequired[LlmReasoningParsingDict | None]
    raw: NotRequired[KvConfigDict | None]


PredictionLoopHandlerUpdate = (
    ProcessingUpdateStatusCreate
    | ProcessingUpdateStatusUpdate
    | ProcessingUpdateStatusRemove
    | ProcessingUpdateCitationBlockCreate
    | ProcessingUpdateDebugInfoBlockCreate
    | ProcessingUpdateContentBlockCreate
    | ProcessingUpdateContentBlockAppendText
    | ProcessingUpdateContentBlockReplaceText
    | ProcessingUpdateContentBlockAppendToolRequest
    | ProcessingUpdateContentBlockReplaceToolRequest
    | ProcessingUpdateContentBlockAppendToolResult
    | ProcessingUpdateContentBlockAttachGenInfo
    | ProcessingUpdateContentBlockSetStyle
    | ProcessingUpdateToolStatusCreate
    | ProcessingUpdateToolStatusUpdate
    | ProcessingUpdateToolStatusArgumentFragment
    | ProcessingUpdateSetSenderName
)
PredictionLoopHandlerUpdateDict = (
    ProcessingUpdateSetSenderNameDict
    | ProcessingUpdateToolStatusArgumentFragmentDict
    | ProcessingUpdateToolStatusUpdateDict
    | ProcessingUpdateToolStatusCreateDict
    | ProcessingUpdateContentBlockSetStyleDict
    | ProcessingUpdateContentBlockAttachGenInfoDict
    | ProcessingUpdateContentBlockAppendToolResultDict
    | ProcessingUpdateContentBlockReplaceToolRequestDict
    | ProcessingUpdateContentBlockAppendToolRequestDict
    | ProcessingUpdateContentBlockReplaceTextDict
    | ProcessingUpdateContentBlockAppendTextDict
    | ProcessingUpdateContentBlockCreateDict
    | ProcessingUpdateDebugInfoBlockCreateDict
    | ProcessingUpdateCitationBlockCreateDict
    | ProcessingUpdateStatusRemoveDict
    | ProcessingUpdateStatusCreateDict
    | ProcessingUpdateStatusUpdateDict
)
ProcessingUpdate = (
    ProcessingUpdateStatusCreate
    | ProcessingUpdateStatusUpdate
    | ProcessingUpdateStatusRemove
    | ProcessingUpdateCitationBlockCreate
    | ProcessingUpdateDebugInfoBlockCreate
    | ProcessingUpdateContentBlockCreate
    | ProcessingUpdateContentBlockAppendText
    | ProcessingUpdateContentBlockAppendToolRequest
    | ProcessingUpdateContentBlockReplaceToolRequest
    | ProcessingUpdateContentBlockAppendToolResult
    | ProcessingUpdateContentBlockReplaceText
    | ProcessingUpdateContentBlockSetPrefix
    | ProcessingUpdateContentBlockSetSuffix
    | ProcessingUpdateContentBlockAttachGenInfo
    | ProcessingUpdateContentBlockSetStyle
    | ProcessingUpdateToolStatusCreate
    | ProcessingUpdateToolStatusUpdate
    | ProcessingUpdateToolStatusArgumentFragment
    | ProcessingUpdateSetSenderName
)
ProcessingUpdateDict = (
    ProcessingUpdateSetSenderNameDict
    | ProcessingUpdateToolStatusArgumentFragmentDict
    | ProcessingUpdateToolStatusUpdateDict
    | ProcessingUpdateToolStatusCreateDict
    | ProcessingUpdateContentBlockSetStyleDict
    | ProcessingUpdateContentBlockAttachGenInfoDict
    | ProcessingUpdateContentBlockSetSuffixDict
    | ProcessingUpdateContentBlockSetPrefixDict
    | ProcessingUpdateContentBlockReplaceTextDict
    | ProcessingUpdateContentBlockAppendToolResultDict
    | ProcessingUpdateContentBlockReplaceToolRequestDict
    | ProcessingUpdateContentBlockAppendToolRequestDict
    | ProcessingUpdateContentBlockAppendTextDict
    | ProcessingUpdateContentBlockCreateDict
    | ProcessingUpdateDebugInfoBlockCreateDict
    | ProcessingUpdateCitationBlockCreateDict
    | ProcessingUpdateStatusRemoveDict
    | ProcessingUpdateStatusCreateDict
    | ProcessingUpdateStatusUpdateDict
)


class ModelManifest(
    LMStudioStruct["ModelManifestDict"], kw_only=True, tag_field="type", tag="model"
):
    type: ClassVar[Annotated[Literal["model"], Meta(title="Type")]] = "model"
    owner: KebabCase
    name: Name
    revision: Revision | None = None
    dependencies: Dependencies | None = None
    tags: Tags | None = None


class ModelManifestDict(TypedDict):
    """Corresponding typed dictionary definition for ModelManifest.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["model"]
    owner: str
    name: str
    revision: NotRequired[int | None]
    dependencies: NotRequired[Dependencies | None]
    tags: NotRequired[Tags | None]


class PluginManifest(
    LMStudioStruct["PluginManifestDict"], kw_only=True, tag_field="type", tag="plugin"
):
    type: ClassVar[Annotated[Literal["plugin"], Meta(title="Type")]] = "plugin"
    runner: PluginRunnerType
    owner: KebabCase
    name: Name
    revision: Revision | None = None
    dependencies: Dependencies | None = None
    tags: Tags | None = None


class PluginManifestDict(TypedDict):
    """Corresponding typed dictionary definition for PluginManifest.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["plugin"]
    runner: PluginRunnerType
    owner: str
    name: str
    revision: NotRequired[int | None]
    dependencies: NotRequired[Dependencies | None]
    tags: NotRequired[Tags | None]


class PresetManifest(
    LMStudioStruct["PresetManifestDict"], kw_only=True, tag_field="type", tag="preset"
):
    type: ClassVar[Annotated[Literal["preset"], Meta(title="Type")]] = "preset"
    owner: KebabCase
    name: Name
    revision: Revision | None = None
    dependencies: Dependencies | None = None
    tags: Tags | None = None


class PresetManifestDict(TypedDict):
    """Corresponding typed dictionary definition for PresetManifest.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["preset"]
    owner: str
    name: str
    revision: NotRequired[int | None]
    dependencies: NotRequired[Dependencies | None]
    tags: NotRequired[Tags | None]


class LlmRpcApplyPromptTemplateParameter(
    LMStudioStruct["LlmRpcApplyPromptTemplateParameterDict"], kw_only=True
):
    specifier: ModelSpecifier
    history: ChatHistoryData
    prediction_config_stack: KvConfigStack = field(name="predictionConfigStack")
    opts: LlmApplyPromptTemplateOpts


class LlmRpcApplyPromptTemplateParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmRpcApplyPromptTemplateParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    specifier: ModelSpecifierDict
    history: ChatHistoryDataDict
    predictionConfigStack: KvConfigStackDict
    opts: LlmApplyPromptTemplateOptsDict


class PseudoLlmRpcApplyPromptTemplate(
    LMStudioStruct["PseudoLlmRpcApplyPromptTemplateDict"], kw_only=True
):
    parameter: LlmRpcApplyPromptTemplateParameter
    returns: LlmRpcApplyPromptTemplateReturns


class PseudoLlmRpcApplyPromptTemplateDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmRpcApplyPromptTemplate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: LlmRpcApplyPromptTemplateParameterDict
    returns: LlmRpcApplyPromptTemplateReturnsDict


class PredictionChannelRequest(
    LMStudioStruct["PredictionChannelRequestDict"], kw_only=True
):
    model_specifier: ModelSpecifier = field(name="modelSpecifier")
    history: ChatHistoryData
    prediction_config_stack: KvConfigStack = field(name="predictionConfigStack")
    fuzzy_preset_identifier: str | None = field(
        name="fuzzyPresetIdentifier", default=None
    )
    ignore_server_session_config: bool | None = field(
        name="ignoreServerSessionConfig", default=None
    )


class PredictionChannelRequestDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelPredictCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    modelSpecifier: ModelSpecifierDict
    history: ChatHistoryDataDict
    predictionConfigStack: KvConfigStackDict
    fuzzyPresetIdentifier: NotRequired[str | None]
    ignoreServerSessionConfig: NotRequired[bool | None]


class PseudoLlmChannelPredict(
    LMStudioStruct["PseudoLlmChannelPredictDict"], kw_only=True
):
    creation_parameter: PredictionChannelRequest = field(name="creationParameter")
    to_client_packet: LlmChannelPredictToClientPacket = field(name="toClientPacket")
    to_server_packet: LlmChannelPredictToServerPacket = field(name="toServerPacket")


class PseudoLlmChannelPredictDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmChannelPredict.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: PredictionChannelRequestDict
    toClientPacket: LlmChannelPredictToClientPacketDict
    toServerPacket: LlmChannelPredictToServerPacketCancelDict


class LlmChannelGenerateWithGeneratorCreationParameter(
    LMStudioStruct["LlmChannelGenerateWithGeneratorCreationParameterDict"], kw_only=True
):
    plugin_identifier: str = field(name="pluginIdentifier")
    plugin_config_stack: KvConfigStack = field(name="pluginConfigStack")
    tools: Sequence[LlmTool]
    working_directory_path: str | None = field(name="workingDirectoryPath")
    history: ChatHistoryData


class LlmChannelGenerateWithGeneratorCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for LlmChannelGenerateWithGeneratorCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pluginIdentifier: str
    pluginConfigStack: KvConfigStackDict
    tools: Sequence[LlmToolFunctionDict]
    workingDirectoryPath: NotRequired[str | None]
    history: ChatHistoryDataDict


class PseudoLlmChannelGenerateWithGenerator(
    LMStudioStruct["PseudoLlmChannelGenerateWithGeneratorDict"], kw_only=True
):
    creation_parameter: LlmChannelGenerateWithGeneratorCreationParameter = field(
        name="creationParameter"
    )
    to_client_packet: LlmChannelGenerateWithGeneratorToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: LlmChannelGenerateWithGeneratorToServerPacket = field(
        name="toServerPacket"
    )


class PseudoLlmChannelGenerateWithGeneratorDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlmChannelGenerateWithGenerator.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: LlmChannelGenerateWithGeneratorCreationParameterDict
    toClientPacket: LlmChannelGenerateWithGeneratorToClientPacketDict
    toServerPacket: LlmChannelGenerateWithGeneratorToServerPacketCancelDict


class PseudoLlm(LMStudioStruct["PseudoLlmDict"], kw_only=True):
    rpc_unload_model: PseudoLlmRpcUnloadModel = field(name="rpcUnloadModel")
    rpc_list_loaded: PseudoLlmRpcListLoaded = field(name="rpcListLoaded")
    rpc_get_model_info: PseudoLlmRpcGetModelInfo = field(name="rpcGetModelInfo")
    rpc_get_load_config: PseudoLlmRpcGetLoadConfig = field(name="rpcGetLoadConfig")
    rpc_apply_prompt_template: PseudoLlmRpcApplyPromptTemplate = field(
        name="rpcApplyPromptTemplate"
    )
    rpc_tokenize: PseudoLlmRpcTokenize = field(name="rpcTokenize")
    rpc_count_tokens: PseudoLlmRpcCountTokens = field(name="rpcCountTokens")
    rpc_preload_draft_model: PseudoLlmRpcPreloadDraftModel = field(
        name="rpcPreloadDraftModel"
    )
    channel_load_model: PseudoLlmChannelLoadModel = field(name="channelLoadModel")
    channel_get_or_load: PseudoLlmChannelGetOrLoad = field(name="channelGetOrLoad")
    channel_predict: PseudoLlmChannelPredict = field(name="channelPredict")
    channel_generate_with_generator: PseudoLlmChannelGenerateWithGenerator = field(
        name="channelGenerateWithGenerator"
    )


class PseudoLlmDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoLlm.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    rpcUnloadModel: PseudoLlmRpcUnloadModelDict
    rpcListLoaded: PseudoLlmRpcListLoadedDict
    rpcGetModelInfo: PseudoLlmRpcGetModelInfoDict
    rpcGetLoadConfig: PseudoLlmRpcGetLoadConfigDict
    rpcApplyPromptTemplate: PseudoLlmRpcApplyPromptTemplateDict
    rpcTokenize: PseudoLlmRpcTokenizeDict
    rpcCountTokens: PseudoLlmRpcCountTokensDict
    rpcPreloadDraftModel: PseudoLlmRpcPreloadDraftModelDict
    channelLoadModel: PseudoLlmChannelLoadModelDict
    channelGetOrLoad: PseudoLlmChannelGetOrLoadDict
    channelPredict: PseudoLlmChannelPredictDict
    channelGenerateWithGenerator: PseudoLlmChannelGenerateWithGeneratorDict


class PluginsRpcProcessingHandleUpdateParameter(
    LMStudioStruct["PluginsRpcProcessingHandleUpdateParameterDict"], kw_only=True
):
    pci: str
    token: str
    update: ProcessingUpdate


class PluginsRpcProcessingHandleUpdateParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingHandleUpdateParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    pci: str
    token: str
    update: ProcessingUpdateDict


class PseudoPluginsRpcProcessingHandleUpdate(
    LMStudioStruct["PseudoPluginsRpcProcessingHandleUpdateDict"], kw_only=True
):
    parameter: PluginsRpcProcessingHandleUpdateParameter


class PseudoPluginsRpcProcessingHandleUpdateDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingHandleUpdate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingHandleUpdateParameterDict


class PluginsRpcProcessingPullHistoryReturns(
    LMStudioStruct["PluginsRpcProcessingPullHistoryReturnsDict"], kw_only=True
):
    messages: Messages


class PluginsRpcProcessingPullHistoryReturnsDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsRpcProcessingPullHistoryReturns.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    messages: Messages


class PseudoPluginsRpcProcessingPullHistory(
    LMStudioStruct["PseudoPluginsRpcProcessingPullHistoryDict"], kw_only=True
):
    parameter: PluginsRpcProcessingPullHistoryParameter
    returns: PluginsRpcProcessingPullHistoryReturns


class PseudoPluginsRpcProcessingPullHistoryDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsRpcProcessingPullHistory.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    parameter: PluginsRpcProcessingPullHistoryParameterDict
    returns: PluginsRpcProcessingPullHistoryReturnsDict


class PluginsChannelRegisterDevelopmentPluginCreationParameter(
    LMStudioStruct["PluginsChannelRegisterDevelopmentPluginCreationParameterDict"],
    kw_only=True,
):
    manifest: PluginManifest


class PluginsChannelRegisterDevelopmentPluginCreationParameterDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelRegisterDevelopmentPluginCreationParameter.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    manifest: PluginManifestDict


class PseudoPluginsChannelRegisterDevelopmentPlugin(
    LMStudioStruct["PseudoPluginsChannelRegisterDevelopmentPluginDict"], kw_only=True
):
    creation_parameter: PluginsChannelRegisterDevelopmentPluginCreationParameter = (
        field(name="creationParameter")
    )
    to_client_packet: PluginsChannelRegisterDevelopmentPluginToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: PluginsChannelRegisterDevelopmentPluginToServerPacket = field(
        name="toServerPacket"
    )


class PseudoPluginsChannelRegisterDevelopmentPluginDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsChannelRegisterDevelopmentPlugin.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    creationParameter: PluginsChannelRegisterDevelopmentPluginCreationParameterDict
    toClientPacket: PluginsChannelRegisterDevelopmentPluginToClientPacketReadyDict
    toServerPacket: PluginsChannelRegisterDevelopmentPluginToServerPacketEndDict


PluginsChannelSetPreprocessorToClientPacket = (
    PluginsChannelSetPreprocessorToClientPacketPreprocess
    | PluginsChannelSetPreprocessorToClientPacketAbort
)
PluginsChannelSetPreprocessorToClientPacketDict = (
    PluginsChannelSetPreprocessorToClientPacketPreprocessDict
    | PluginsChannelSetPreprocessorToClientPacketAbortDict
)
PluginsChannelSetPreprocessorToServerPacket = (
    PluginsChannelSetPreprocessorToServerPacketComplete
    | PluginsChannelSetPreprocessorToServerPacketAborted
    | PluginsChannelSetPreprocessorToServerPacketError
)
PluginsChannelSetPreprocessorToServerPacketDict = (
    PluginsChannelSetPreprocessorToServerPacketErrorDict
    | PluginsChannelSetPreprocessorToServerPacketCompleteDict
    | PluginsChannelSetPreprocessorToServerPacketAbortedDict
)


class PseudoPluginsChannelSetPreprocessor(
    LMStudioStruct["PseudoPluginsChannelSetPreprocessorDict"], kw_only=True
):
    to_client_packet: PluginsChannelSetPreprocessorToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: PluginsChannelSetPreprocessorToServerPacket = field(
        name="toServerPacket"
    )


class PseudoPluginsChannelSetPreprocessorDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsChannelSetPreprocessor.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    toClientPacket: PluginsChannelSetPreprocessorToClientPacketDict
    toServerPacket: PluginsChannelSetPreprocessorToServerPacketDict


class PluginsChannelSetGeneratorToClientPacketGenerate(
    LMStudioStruct["PluginsChannelSetGeneratorToClientPacketGenerateDict"],
    kw_only=True,
    tag_field="type",
    tag="generate",
):
    type: ClassVar[Annotated[Literal["generate"], Meta(title="Type")]] = "generate"
    task_id: str = field(name="taskId")
    input: PluginsRpcProcessingPullHistoryReturns
    plugin_config: LlmRpcGetLoadConfigReturns = field(name="pluginConfig")
    global_plugin_config: LlmRpcGetLoadConfigReturns = field(name="globalPluginConfig")
    tool_definitions: Sequence[LlmTool] = field(name="toolDefinitions")
    working_directory_path: str | None = field(name="workingDirectoryPath")


class PluginsChannelSetGeneratorToClientPacketGenerateDict(TypedDict):
    """Corresponding typed dictionary definition for PluginsChannelSetGeneratorToClientPacketGenerate.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    type: Literal["generate"]
    taskId: str
    input: PluginsRpcProcessingPullHistoryReturnsDict
    pluginConfig: LlmRpcGetLoadConfigReturnsDict
    globalPluginConfig: LlmRpcGetLoadConfigReturnsDict
    toolDefinitions: Sequence[LlmToolFunctionDict]
    workingDirectoryPath: NotRequired[str | None]


ArtifactManifest = PluginManifest | PresetManifest | ModelManifest
ArtifactManifestDict = ModelManifestDict | PluginManifestDict | PresetManifestDict
PluginsChannelSetGeneratorToClientPacket = (
    PluginsChannelSetGeneratorToClientPacketGenerate
    | PluginsChannelSetGeneratorToClientPacketAbort
)
PluginsChannelSetGeneratorToClientPacketDict = (
    PluginsChannelSetGeneratorToClientPacketGenerateDict
    | PluginsChannelSetGeneratorToClientPacketAbortDict
)


class PseudoPluginsChannelSetGenerator(
    LMStudioStruct["PseudoPluginsChannelSetGeneratorDict"], kw_only=True
):
    to_client_packet: PluginsChannelSetGeneratorToClientPacket = field(
        name="toClientPacket"
    )
    to_server_packet: PluginsChannelSetGeneratorToServerPacket = field(
        name="toServerPacket"
    )


class PseudoPluginsChannelSetGeneratorDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPluginsChannelSetGenerator.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    toClientPacket: PluginsChannelSetGeneratorToClientPacketDict
    toServerPacket: PluginsChannelSetGeneratorToServerPacketDict


class PseudoPlugins(LMStudioStruct["PseudoPluginsDict"], kw_only=True):
    rpc_reindex_plugins: PseudoPluginsRpcReindexPlugins = field(
        name="rpcReindexPlugins"
    )
    rpc_processing_handle_update: PseudoPluginsRpcProcessingHandleUpdate = field(
        name="rpcProcessingHandleUpdate"
    )
    rpc_processing_handle_request: PseudoPluginsRpcProcessingHandleRequest = field(
        name="rpcProcessingHandleRequest"
    )
    rpc_processing_pull_history: PseudoPluginsRpcProcessingPullHistory = field(
        name="rpcProcessingPullHistory"
    )
    rpc_processing_get_or_load_model: PseudoPluginsRpcProcessingGetOrLoadModel = field(
        name="rpcProcessingGetOrLoadModel"
    )
    rpc_processing_has_status: PseudoPluginsRpcProcessingHasStatus = field(
        name="rpcProcessingHasStatus"
    )
    rpc_processing_needs_naming: PseudoPluginsRpcProcessingNeedsNaming = field(
        name="rpcProcessingNeedsNaming"
    )
    rpc_processing_suggest_name: PseudoPluginsRpcProcessingSuggestName = field(
        name="rpcProcessingSuggestName"
    )
    rpc_processing_set_sender_name: PseudoPluginsRpcProcessingSetSenderName = field(
        name="rpcProcessingSetSenderName"
    )
    rpc_set_config_schematics: PseudoPluginsRpcSetConfigSchematics = field(
        name="rpcSetConfigSchematics"
    )
    rpc_set_global_config_schematics: PseudoPluginsRpcSetGlobalConfigSchematics = field(
        name="rpcSetGlobalConfigSchematics"
    )
    rpc_plugin_init_completed: PseudoPluginsRpcPluginInitCompleted = field(
        name="rpcPluginInitCompleted"
    )
    channel_register_development_plugin: PseudoPluginsChannelRegisterDevelopmentPlugin = field(
        name="channelRegisterDevelopmentPlugin"
    )
    channel_set_preprocessor: PseudoPluginsChannelSetPreprocessor = field(
        name="channelSetPreprocessor"
    )
    channel_set_prediction_loop_handler: PseudoPluginsChannelSetPredictionLoopHandler = field(
        name="channelSetPredictionLoopHandler"
    )
    channel_set_tools_provider: PseudoPluginsChannelSetToolsProvider = field(
        name="channelSetToolsProvider"
    )
    channel_set_generator: PseudoPluginsChannelSetGenerator = field(
        name="channelSetGenerator"
    )


class PseudoPluginsDict(TypedDict):
    """Corresponding typed dictionary definition for PseudoPlugins.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    rpcReindexPlugins: PseudoPluginsRpcReindexPlugins
    rpcProcessingHandleUpdate: PseudoPluginsRpcProcessingHandleUpdateDict
    rpcProcessingHandleRequest: PseudoPluginsRpcProcessingHandleRequestDict
    rpcProcessingPullHistory: PseudoPluginsRpcProcessingPullHistoryDict
    rpcProcessingGetOrLoadModel: PseudoPluginsRpcProcessingGetOrLoadModelDict
    rpcProcessingHasStatus: PseudoPluginsRpcProcessingHasStatusDict
    rpcProcessingNeedsNaming: PseudoPluginsRpcProcessingNeedsNamingDict
    rpcProcessingSuggestName: PseudoPluginsRpcProcessingSuggestNameDict
    rpcProcessingSetSenderName: PseudoPluginsRpcProcessingSetSenderNameDict
    rpcSetConfigSchematics: PseudoPluginsRpcSetConfigSchematicsDict
    rpcSetGlobalConfigSchematics: PseudoPluginsRpcSetGlobalConfigSchematicsDict
    rpcPluginInitCompleted: PseudoPluginsRpcPluginInitCompleted
    channelRegisterDevelopmentPlugin: PseudoPluginsChannelRegisterDevelopmentPluginDict
    channelSetPreprocessor: PseudoPluginsChannelSetPreprocessorDict
    channelSetPredictionLoopHandler: PseudoPluginsChannelSetPredictionLoopHandlerDict
    channelSetToolsProvider: PseudoPluginsChannelSetToolsProviderDict
    channelSetGenerator: PseudoPluginsChannelSetGeneratorDict


class Model(LMStudioStruct["ModelDict"], kw_only=True):
    diagnostics: PseudoDiagnostics
    embedding: PseudoEmbedding
    files: PseudoFiles
    llm: PseudoLlm
    plugins: PseudoPlugins
    repository: PseudoRepository
    system: PseudoSystem


class ModelDict(TypedDict):
    """Corresponding typed dictionary definition for Model.

    NOTE: Multi-word keys are defined using their camelCase form,
    as that is what `to_dict()` emits, and what `_from_api_dict()` accepts.
    """

    diagnostics: PseudoDiagnosticsDict
    embedding: PseudoEmbeddingDict
    files: PseudoFilesDict
    llm: PseudoLlmDict
    plugins: PseudoPluginsDict
    repository: PseudoRepositoryDict
    system: PseudoSystemDict

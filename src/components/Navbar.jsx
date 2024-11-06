import {
  Box,
  Flex,
  Button,
  useColorModeValue,
  HStack,
  useDisclosure,
  IconButton,
  Heading,
  Stack,
} from "@chakra-ui/react";
import { HamburgerIcon, CloseIcon } from "@chakra-ui/icons";

export default function Navbar() {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <Box 
      position="sticky" 
      top="0" 
      zIndex="1000"
      bg={useColorModeValue("white", "gray.800")}
      borderBottom="1px"
      borderColor={useColorModeValue("gray.200", "gray.700")}
    >
      <Flex
        h={16}
        alignItems="center"
        justifyContent="space-between"
        mx="auto"
        px={8}
      >
        <HStack spacing={8} alignItems="center">
          <Heading size="md">CargoPrism Dashboard</Heading>
        </HStack>

        <Flex alignItems="center">
          <HStack
            as="nav"
            spacing={4}
            display={{ base: "none", md: "flex" }}
          >
            <Button variant="ghost">
              <a href="/">Dashboard</a>
            </Button>
            <Button variant="ghost">
              <a href="/shipments">Shipments</a>
            </Button>
            <Button variant="ghost">
              <a href="/analytics">Analytics</a>
            </Button>
          </HStack>

          <IconButton
            size="md"
            icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
            aria-label="Open Menu"
            display={{ md: "none" }}
            onClick={isOpen ? onClose : onOpen}
            ml={4}
          />
        </Flex>
      </Flex>

      {/* Mobile menu */}
      {isOpen && (
        <Box pb={4} display={{ md: "none" }} px={4}>
          <Stack as="nav" spacing={4}>
            <Button variant="ghost" w="full">
              <a href="/">Dashboard</a>
            </Button>
            <Button variant="ghost" w="full">
              <a href="/shipments">Shipments</a>
            </Button>
            <Button variant="ghost" w="full">
              <a href="/analytics">Analytics</a>
            </Button>
          </Stack>
        </Box>
      )}
    </Box>
  );
}